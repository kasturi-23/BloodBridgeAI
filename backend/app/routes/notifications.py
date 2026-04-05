from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.schemas.notification import NotificationGenerateIn, NotificationSendIn
from app.services.ai_service import generate_outreach_message
from app.utils.serializers import serialize_doc

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/generate")
async def generate_notification(payload: NotificationGenerateIn, db=Depends(get_db)):
    donor = serialize_doc(await db.donors.find_one({"donor_id": payload.donor_id}))
    request_doc = serialize_doc(await db.requests.find_one({"request_id": payload.request_id}))

    if not donor or not request_doc:
        raise HTTPException(status_code=404, detail="Donor or request not found")

    message = await generate_outreach_message(payload.channel, donor, request_doc)
    return {
        "donor_id": payload.donor_id,
        "request_id": payload.request_id,
        "channel": payload.channel,
        "generated_message": message,
    }


@router.post("/send")
async def send_notification(payload: NotificationSendIn, db=Depends(get_db)):
    donor = serialize_doc(await db.donors.find_one({"donor_id": payload.donor_id}))
    request_doc = serialize_doc(await db.requests.find_one({"request_id": payload.request_id}))

    if not donor or not request_doc:
        raise HTTPException(status_code=404, detail="Donor or request not found")

    notification_doc = {
        "notification_id": str(uuid4()),
        "donor_id": payload.donor_id,
        "request_id": payload.request_id,
        "channel": payload.channel,
        "generated_message": payload.generated_message,
        "sent_status": "sent",
        "sent_at": datetime.utcnow(),
    }
    await db.notifications.insert_one(notification_doc)
    await db.donors.update_one(
        {"donor_id": payload.donor_id},
        {"$set": {"contacted": True, "updated_at": datetime.utcnow()}},
    )

    return {
        "message": "Notification sent (simulated)",
        "notification": serialize_doc(notification_doc),
    }


@router.get("")
async def list_notifications(db=Depends(get_db)):
    rows = await db.notifications.find().sort("sent_at", -1).to_list(length=200)
    return [serialize_doc(r) for r in rows]
