from datetime import datetime, timedelta

from app.utils.blood_compatibility import compatibility_strength, is_compatible
from app.utils.geo import haversine_miles

MIN_DONATION_GAP_DAYS = 90


def _normalize_distance_score(distance_miles: float, radius_limit: float) -> float:
    if distance_miles <= 0:
        return 1.0
    capped = min(distance_miles, radius_limit)
    return round(max(0.0, 1 - (capped / radius_limit)), 4)


def _recommendation_tag(score: float, distance_miles: float, response_rate: float, idx: int) -> str:
    if idx == 0 or score >= 0.86:
        return "Best Match"
    if response_rate >= 0.75:
        return "Highly Responsive"
    if distance_miles <= 5:
        return "Nearby"
    return "Backup Donor"


async def match_donors_for_request(db, request_doc: dict, max_results: int = 25):
    blood_type_needed = request_doc["blood_type_needed"]
    urgency = request_doc["urgency_level"]
    hospital_lat = request_doc["hospital_latitude"]
    hospital_lon = request_doc["hospital_longitude"]

    base_radius = 10
    expanded_radius = 35
    radius_limit = base_radius

    base_query = {
        "eligibility_status": "eligible",
        "health_screening_status": "passed",
        "availability_status": "available",
        "age": {"$gte": 18, "$lte": 65},
    }

    donors = await db.donors.find(base_query).to_list(length=500)
    now = datetime.utcnow()

    def build_ranked_candidates(radius: float):
        ranked: list[dict] = []
        for donor in donors:
            if not is_compatible(donor["blood_group"], blood_type_needed):
                continue

            last_donation_date = donor.get("last_donation_date")
            if isinstance(last_donation_date, str):
                last_donation_date = datetime.fromisoformat(last_donation_date)
            if not last_donation_date or (now - last_donation_date) < timedelta(days=MIN_DONATION_GAP_DAYS):
                continue

            distance_miles = haversine_miles(hospital_lat, hospital_lon, donor["latitude"], donor["longitude"])
            if distance_miles > radius:
                continue

            compatibility_score = compatibility_strength(donor["blood_group"], blood_type_needed)
            distance_score = _normalize_distance_score(distance_miles, radius)
            availability_score = 1.0 if donor["availability_status"] == "available" else 0.4
            response_score = float(donor.get("past_response_rate", 0.0))
            donation_reliability = min(1.0, donor.get("total_donations", 0) / 20)

            if urgency == "Critical":
                weights = (0.35, 0.20, 0.15, 0.20, 0.10)
            elif urgency == "High":
                weights = (0.40, 0.25, 0.15, 0.12, 0.08)
            else:
                weights = (0.40, 0.25, 0.15, 0.10, 0.10)

            score = (
                compatibility_score * weights[0]
                + distance_score * weights[1]
                + availability_score * weights[2]
                + response_score * weights[3]
                + donation_reliability * weights[4]
            )

            if urgency == "Critical" and response_score >= 0.8:
                score += 0.03

            ranked.append(
                {
                    "donor_id": donor["donor_id"],
                    "full_name": donor["full_name"],
                    "blood_group": donor["blood_group"],
                    "city": donor["city"],
                    "distance_miles": round(distance_miles, 2),
                    "eligibility_status": donor["eligibility_status"],
                    "availability_status": donor["availability_status"],
                    "response_probability": round(response_score, 2),
                    "ranking_score": round(min(score, 1.0), 4),
                }
            )

        ranked.sort(key=lambda x: x["ranking_score"], reverse=True)
        for idx, item in enumerate(ranked):
            item["recommendation_tag"] = _recommendation_tag(
                item["ranking_score"], item["distance_miles"], item["response_probability"], idx
            )
        return ranked[:max_results]

    ranked = build_ranked_candidates(base_radius)
    if len(ranked) < 5:
        radius_limit = expanded_radius
        ranked = build_ranked_candidates(expanded_radius)

    return ranked, radius_limit
