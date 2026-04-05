from fastapi import APIRouter, Depends

from app.database import get_db
from app.utils.blood_compatibility import ALL_BLOOD_GROUPS

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary")
async def analytics_summary(db=Depends(get_db)):
    total_donors = await db.donors.count_documents({})
    available_donors = await db.donors.count_documents({"availability_status": "available"})
    eligible_donors = await db.donors.count_documents({"eligibility_status": "eligible"})

    active_requests = await db.requests.count_documents({"status": {"$in": ["pending", "in_progress"]}})
    fulfilled_requests = await db.requests.count_documents({"status": "fulfilled"})
    pending_requests = await db.requests.count_documents({"status": "pending"})

    recent_matches = await db.requests.find().sort("created_at", -1).limit(10).to_list(length=10)
    recent_responses = await db.notifications.find().sort("sent_at", -1).limit(10).to_list(length=10)

    donor_rows = await db.donors.find({}, {"past_response_rate": 1}).to_list(length=500)
    avg_response_rate = round(
        sum(float(d.get("past_response_rate", 0)) for d in donor_rows) / max(len(donor_rows), 1),
        3,
    )

    urgent_alerts = await db.requests.count_documents({"urgency_level": {"$in": ["High", "Critical"]}, "status": "pending"})

    blood_type_demand = {}
    for bg in ALL_BLOOD_GROUPS:
        blood_type_demand[bg] = await db.requests.count_documents({"blood_type_needed": bg})

    availability_stats = {
        "available": await db.donors.count_documents({"availability_status": "available"}),
        "unavailable": await db.donors.count_documents({"availability_status": "unavailable"}),
        "busy": await db.donors.count_documents({"availability_status": "busy"}),
    }

    city_pipeline = [{"$group": {"_id": "$city", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}, {"$limit": 6}]
    top_cities = [{"city": row["_id"], "count": row["count"]} async for row in db.donors.aggregate(city_pipeline)]

    urgent_pipeline = [
        {"$match": {"urgency_level": {"$in": ["High", "Critical"]}}},
        {
            "$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id": 1}},
        {"$limit": 15},
    ]
    urgent_trends = [{"date": r["_id"], "count": r["count"]} async for r in db.requests.aggregate(urgent_pipeline)]

    return {
        "metrics": {
            "total_donors": total_donors,
            "available_donors": available_donors,
            "eligible_donors": eligible_donors,
            "active_requests": active_requests,
            "fulfilled_requests": fulfilled_requests,
            "pending_requests": pending_requests,
            "recent_donor_matches": len(recent_matches),
            "recent_donor_responses": len(recent_responses),
            "average_response_rate": avg_response_rate,
            "urgent_request_alerts": urgent_alerts,
        },
        "blood_type_demand": blood_type_demand,
        "availability_stats": availability_stats,
        "top_cities": top_cities,
        "urgent_request_trends": urgent_trends,
    }
