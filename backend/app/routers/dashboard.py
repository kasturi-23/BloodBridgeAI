from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.database import get_db
from app.models.hospital_request import HospitalRequest
from app.models.call_response import CallResponse
from app.models.donor import Donor
from app.schemas.hospital_request import DashboardPayload, DashboardDonorCard, RequestOut

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def build_donor_card(record: CallResponse, donor: Donor, distance_km=None) -> DashboardDonorCard:
    return DashboardDonorCard(
        call_response_id=record.call_response_id,
        donor_id=donor.donor_id,
        full_name=donor.full_name,
        blood_group=donor.blood_group,
        phone_number=donor.phone_number,
        distance_km=distance_km,
        call_status=record.call_status,
        eta_minutes=record.eta_minutes,
        fit_to_donate_today=record.fit_to_donate_today,
        map_sent=record.map_sent,
        location_consent=record.location_consent,
        rank_position=record.rank_position,
        ineligibility_reason=record.ineligibility_reason,
        response_timestamp=record.response_timestamp,
    )


@router.get("/{request_id}", response_model=DashboardPayload)
def get_dashboard(request_id: UUID, db: Session = Depends(get_db)):
    """Return full dashboard payload for a blood request."""
    request = db.query(HospitalRequest).filter(
        HospitalRequest.request_id == request_id
    ).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    call_records: List[CallResponse] = (
        db.query(CallResponse)
        .filter(CallResponse.request_id == request_id)
        .order_by(CallResponse.rank_position.nullslast(), CallResponse.created_at)
        .all()
    )

    confirmed, standby, pending_donors, declined = [], [], [], []

    for record in call_records:
        donor = db.query(Donor).filter(Donor.donor_id == record.donor_id).first()
        if not donor:
            continue

        card = build_donor_card(record, donor)

        if record.call_status == "accepted":
            confirmed.append(card)
        elif record.call_status in ("declined", "no_answer", "ineligible", "call_ended"):
            declined.append(card)
        elif record.call_status in ("pending", "calling"):
            pending_donors.append(card)
        else:
            standby.append(card)

    # Standby = accepted donors beyond the required units
    units_needed = request.units_needed
    if len(confirmed) > units_needed:
        standby = confirmed[units_needed:]
        confirmed = confirmed[:units_needed]

    return DashboardPayload(
        request=RequestOut.model_validate(request),
        confirmed_donors=confirmed,
        standby_donors=standby,
        pending_donors=pending_donors,
        declined_donors=declined,
        total_donors_contacted=len(
            [r for r in call_records if r.call_status not in ("pending", "ineligible")]
        ),
    )


@router.get("/", response_model=List[RequestOut])
def list_active_requests(db: Session = Depends(get_db)):
    """Return all open/in-progress requests for the main dashboard overview."""
    return (
        db.query(HospitalRequest)
        .filter(HospitalRequest.request_status.in_(["open", "in_progress", "donor_confirmed"]))
        .order_by(HospitalRequest.created_at.desc())
        .all()
    )
