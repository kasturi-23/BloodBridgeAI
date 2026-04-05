"""
Matching Agent
Responsibility: Find compatible nearby donors for a hospital blood request.
Inputs: Request details, donor blood group, donor location, active status.
Outputs: Shortlisted compatible donors with distance scores.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from geopy.distance import geodesic
import logging

from app.models.donor import Donor
from app.models.hospital_request import HospitalRequest
from app.config import settings

logger = logging.getLogger(__name__)

# Blood compatibility matrix: key = requested blood group, value = compatible donor groups
BLOOD_COMPATIBILITY: Dict[str, List[str]] = {
    "O-":  ["O-"],
    "O+":  ["O-", "O+"],
    "A-":  ["O-", "A-"],
    "A+":  ["O-", "O+", "A-", "A+"],
    "B-":  ["O-", "B-"],
    "B+":  ["O-", "O+", "B-", "B+"],
    "AB-": ["O-", "A-", "B-", "AB-"],
    "AB+": ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],
}


class MatchingAgent:
    """
    Agent 1: Find compatible donors within radius, ranked by proximity and score.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_compatible_groups(self, blood_group_needed: str) -> List[str]:
        return BLOOD_COMPATIBILITY.get(blood_group_needed.upper(), [blood_group_needed.upper()])

    def calculate_distance(
        self,
        hospital_lat: float,
        hospital_lng: float,
        donor_lat: Optional[float],
        donor_lng: Optional[float],
    ) -> Optional[float]:
        if donor_lat is None or donor_lng is None:
            return None
        try:
            return geodesic((hospital_lat, hospital_lng), (donor_lat, donor_lng)).km
        except Exception:
            return None

    def run(
        self,
        request: HospitalRequest,
        radius_km: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Find and shortlist compatible, active donors within the search radius.
        Returns list of dicts with donor + distance_km.
        """
        if radius_km is None:
            radius_km = settings.DEFAULT_SEARCH_RADIUS_KM

        compatible_groups = self.get_compatible_groups(request.blood_group_needed)
        logger.info(
            f"[MatchingAgent] Request {request.request_id}: "
            f"Need {request.blood_group_needed}, compatible donors: {compatible_groups}"
        )

        # Query active donors with compatible blood groups
        donors: List[Donor] = (
            self.db.query(Donor)
            .filter(
                Donor.is_active == True,
                Donor.availability_status == "available",
                Donor.blood_group.in_(compatible_groups),
            )
            .all()
        )

        shortlist = []
        no_location_donors = []

        for donor in donors:
            distance = self.calculate_distance(
                request.hospital_latitude,
                request.hospital_longitude,
                donor.latitude,
                donor.longitude,
            )

            if distance is None:
                # Include donors without location but deprioritize
                no_location_donors.append({
                    "donor": donor,
                    "distance_km": None,
                    "score": donor.past_response_score * 0.3,
                })
            elif distance <= radius_km:
                # Score = response_score (0-1) weighted with inverse distance
                distance_score = max(0.0, 1.0 - (distance / radius_km))
                combined_score = (donor.past_response_score * 0.6) + (distance_score * 0.4)
                shortlist.append({
                    "donor": donor,
                    "distance_km": round(distance, 2),
                    "score": round(combined_score, 4),
                })

        # Sort by score descending
        shortlist.sort(key=lambda x: x["score"], reverse=True)
        no_location_donors.sort(key=lambda x: x["score"], reverse=True)

        result = shortlist + no_location_donors

        logger.info(
            f"[MatchingAgent] Found {len(result)} compatible donors "
            f"({len(shortlist)} within {radius_km}km radius)"
        )
        return result

    def expand_radius_and_run(self, request: HospitalRequest) -> List[Dict[str, Any]]:
        """Retry with expanded radius up to MAX_SEARCH_RADIUS_KM."""
        for radius in [settings.DEFAULT_SEARCH_RADIUS_KM * 2, settings.MAX_SEARCH_RADIUS_KM]:
            result = self.run(request, radius_km=radius)
            if result:
                logger.info(f"[MatchingAgent] Found donors at expanded radius {radius}km")
                return result
        return []
