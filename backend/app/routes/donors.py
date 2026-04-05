from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query

from app.database import get_db
from app.schemas.donor import DonorOut, DonorUpdate
from app.utils.geo import haversine_miles
from app.utils.serializers import serialize_doc

router = APIRouter(prefix="/donors", tags=["Donors"])


@router.get("", response_model=list[DonorOut])
async def list_donors(
    blood_group: str | None = None,
    city: str | None = None,
    eligibility: str | None = None,
    availability: str | None = None,
    screening: str | None = None,
    min_response_rate: float | None = Query(default=None, ge=0, le=1),
    radius_miles: float | None = Query(default=None, gt=0),
    hospital_latitude: float | None = None,
    hospital_longitude: float | None = None,
    db=Depends(get_db),
):
    query = {}
    if blood_group:
        query["blood_group"] = blood_group
    if city:
        query["city"] = city
    if eligibility:
        query["eligibility_status"] = eligibility
    if availability:
        query["availability_status"] = availability
    if screening:
        query["health_screening_status"] = screening
    if min_response_rate is not None:
        query["past_response_rate"] = {"$gte": min_response_rate}

    donors = [serialize_doc(d) for d in await db.donors.find(query).sort("created_at", -1).to_list(length=500)]

    if radius_miles and hospital_latitude is not None and hospital_longitude is not None:
        donors = [
            d
            for d in donors
            if haversine_miles(hospital_latitude, hospital_longitude, d["latitude"], d["longitude"]) <= radius_miles
        ]

    return donors


@router.get("/{donor_id}", response_model=DonorOut)
async def get_donor(donor_id: str, db=Depends(get_db)):
    donor = serialize_doc(await db.donors.find_one({"donor_id": donor_id}))
    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found")
    return donor


@router.put("/{donor_id}", response_model=DonorOut)
async def update_donor(donor_id: str, payload: DonorUpdate, db=Depends(get_db)):
    donor = await db.donors.find_one({"donor_id": donor_id})
    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found")

    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not update_data:
        return serialize_doc(donor)

    update_data["updated_at"] = datetime.utcnow()
    await db.donors.update_one({"donor_id": donor_id}, {"$set": update_data})
    updated = serialize_doc(await db.donors.find_one({"donor_id": donor_id}))
    return updated
