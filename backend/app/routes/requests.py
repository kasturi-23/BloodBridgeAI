from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.schemas.blood_request import BloodRequestCreate, BloodRequestOut
from app.services.ai_service import generate_match_summary
from app.services.matching import match_donors_for_request
from app.utils.serializers import serialize_doc

router = APIRouter(prefix="/requests", tags=["Requests"])


@router.post("", response_model=BloodRequestOut)
async def create_request(payload: BloodRequestCreate, db=Depends(get_db)):
    request_doc = payload.model_dump()
    request_doc.update(
        {
            "request_id": str(uuid4()),
            "status": "pending",
            "created_at": datetime.utcnow(),
        }
    )
    await db.requests.insert_one(request_doc)
    return serialize_doc(request_doc)


@router.get("", response_model=list[BloodRequestOut])
async def list_requests(db=Depends(get_db)):
    rows = await db.requests.find().sort("created_at", -1).to_list(length=200)
    return [serialize_doc(r) for r in rows]


@router.get("/{request_id}", response_model=BloodRequestOut)
async def get_request(request_id: str, db=Depends(get_db)):
    request_doc = serialize_doc(await db.requests.find_one({"request_id": request_id}))
    if not request_doc:
        raise HTTPException(status_code=404, detail="Request not found")
    return request_doc


@router.get("/{request_id}/matches")
async def get_request_matches(request_id: str, db=Depends(get_db)):
    request_doc = serialize_doc(await db.requests.find_one({"request_id": request_id}))
    if not request_doc:
        raise HTTPException(status_code=404, detail="Request not found")

    matches, radius = await match_donors_for_request(db, request_doc)
    summary = await generate_match_summary(request_doc, matches)

    return {
        "request": request_doc,
        "search_radius_miles": radius,
        "total_matches": len(matches),
        "top_matches": matches[:5],
        "matches": matches,
        "ai_summary": summary,
    }
