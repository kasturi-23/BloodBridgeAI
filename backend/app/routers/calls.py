from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Form, BackgroundTasks
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
import logging

from app.database import get_db
from app.models.call_response import CallResponse
from app.models.hospital_request import HospitalRequest
from app.models.donor import Donor
from app.agents.call_assistant_agent import CallAssistantAgent
from app.services.twilio_service import TwilioService
from app.services.sms_service import SMSService
from app.services.transcript_analysis_service import TranscriptAnalysisService
from app.schemas.call_response import ManualOverridePayload

router = APIRouter(prefix="/api/call", tags=["calls"])
logger = logging.getLogger(__name__)


@router.post("/start/{request_id}")
def start_outreach(
    request_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Manually start or resume donor outreach for a request."""
    request = db.query(HospitalRequest).filter(
        HospitalRequest.request_id == request_id
    ).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    next_record = (
        db.query(CallResponse)
        .filter(
            CallResponse.request_id == request_id,
            CallResponse.call_status == "pending",
        )
        .order_by(CallResponse.rank_position)
        .first()
    )

    if not next_record:
        return {"message": "No pending donors to call", "request_id": str(request_id)}

    def _call(record_id):
        record = db.query(CallResponse).filter(
            CallResponse.call_response_id == record_id
        ).first()
        if not record:
            return
        req = db.query(HospitalRequest).filter(
            HospitalRequest.request_id == record.request_id
        ).first()
        agent = CallAssistantAgent(db, TwilioService(), SMSService())
        agent.initiate_call(req, record)

    background_tasks.add_task(_call, next_record.call_response_id)
    donor = db.query(Donor).filter(Donor.donor_id == next_record.donor_id).first()
    return {
        "message": "Call initiated",
        "donor_name": donor.full_name if donor else "Unknown",
        "call_response_id": str(next_record.call_response_id),
    }


@router.post("/webhook")
async def call_webhook(
    request: Request,
    request_id: Optional[str] = None,
    call_response_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Receive Bland.ai post-call webhook.
    Bland.ai POSTs JSON when a call ends with transcript, status, and metadata.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}

    logger.info(f"[Webhook] Bland.ai callback received: {body}")

    # Resolve IDs from query params or metadata embedded in the payload
    metadata = body.get("metadata") or {}
    resolved_request_id = request_id or metadata.get("request_id")
    resolved_call_response_id = call_response_id or metadata.get("call_response_id")

    if not resolved_call_response_id:
        logger.warning("[Webhook] No call_response_id — ignoring")
        return {"status": "ignored"}

    record = db.query(CallResponse).filter(
        CallResponse.call_response_id == resolved_call_response_id
    ).first()
    if not record:
        logger.warning(f"[Webhook] CallResponse {resolved_call_response_id} not found")
        return {"status": "not_found"}

    # Determine outcome from Bland.ai fields
    call_status = body.get("status", "")      # completed, no-answer, busy, failed
    answered_by = body.get("answered_by", "") # human, voicemail, unknown
    transcript = body.get("transcript", "") or ""
    summary = body.get("summary", "") or ""

    agent = CallAssistantAgent(db, TwilioService(), SMSService())

    # No-answer / voicemail / failed → mark and move on
    if call_status in ("no-answer", "busy", "failed") or answered_by == "voicemail":
        agent.process_no_answer(record)
        _call_next_donor(record.request_id, db)
        return {"status": "no_answer"}

    # Use GPT to analyze the full transcript and make the decision
    analysis = TranscriptAnalysisService().analyze(transcript, summary)
    logger.info(f"[Webhook] GPT analysis for donor {record.donor_id}: {analysis}")

    accepted = analysis.get("accepted")
    eta_minutes = analysis.get("eta_minutes")
    fit_to_donate = analysis.get("fit_to_donate")
    decline_reason = analysis.get("decline_reason")

    if accepted is True:
        agent.process_acceptance(
            call_record=record,
            eta_minutes=eta_minutes,
            fit_to_donate=fit_to_donate if fit_to_donate is not None else True,
            medication_response=None,
            location_consent=False,
        )
        logger.info(f"[Webhook] GPT decision: donor {record.donor_id} ACCEPTED — ETA {eta_minutes} min")
        return {"status": "accepted"}
    elif accepted is False:
        agent.process_declination(record, reason=decline_reason or "Donor declined")
        _call_next_donor(record.request_id, db)
        logger.info(f"[Webhook] GPT decision: donor {record.donor_id} DECLINED — {decline_reason}")
        return {"status": "declined"}
    else:
        # GPT couldn't determine — call ended without a clear answer
        record.call_status = "call_ended"
        record.response_timestamp = datetime.utcnow()
        db.commit()
        _call_next_donor(record.request_id, db)
        logger.info(f"[Webhook] GPT decision: donor {record.donor_id} — ambiguous, marked call_ended")
        return {"status": "call_ended"}


@router.post("/simulate/{call_response_id}")
def simulate_call_outcome(
    call_response_id: UUID,
    payload: ManualOverridePayload,
    db: Session = Depends(get_db),
):
    """
    Development endpoint to simulate a call outcome without real Twilio call.
    """
    record = db.query(CallResponse).filter(
        CallResponse.call_response_id == call_response_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Call record not found")

    agent = CallAssistantAgent(db, None, SMSService())

    if payload.call_status == "accepted":
        agent.process_acceptance(
            call_record=record,
            eta_minutes=payload.eta_minutes,
            fit_to_donate=True,
            medication_response=None,
            location_consent=False,
        )
    elif payload.call_status == "declined":
        agent.process_declination(record, reason=payload.notes)
        _call_next_donor(record.request_id, db)
    elif payload.call_status == "no_answer":
        agent.process_no_answer(record)
        _call_next_donor(record.request_id, db)
    else:
        raise HTTPException(status_code=400, detail="Invalid call_status for simulation")

    db.refresh(record)
    return {
        "call_response_id": str(record.call_response_id),
        "call_status": record.call_status,
        "eta_minutes": record.eta_minutes,
        "map_sent": record.map_sent,
    }


def _call_next_donor(request_id, db: Session):
    """
    After a decline/no-answer, check if all active calls are done.
    If no one accepted, auto-expand radius and call next 5 donors.
    """
    from app.agents.matching_agent import MatchingAgent
    from app.agents.eligibility_agent import EligibilityAgent
    from app.config import settings

    request = db.query(HospitalRequest).filter(
        HospitalRequest.request_id == request_id
    ).first()
    if not request or request.request_status in ("donor_confirmed", "closed", "failed"):
        return

    still_active = db.query(CallResponse).filter(
        CallResponse.request_id == request_id,
        CallResponse.call_status.in_(["pending", "calling"]),
    ).first()
    if still_active:
        return

    has_accepted = db.query(CallResponse).filter(
        CallResponse.request_id == request_id,
        CallResponse.call_status == "accepted",
    ).first()
    if has_accepted:
        return

    already_called_ids = [
        str(r.donor_id) for r in db.query(CallResponse)
        .filter(CallResponse.request_id == request_id).all()
    ]

    current_radius = request.search_radius_km or settings.DEFAULT_SEARCH_RADIUS_KM
    expansion_steps = [settings.DEFAULT_SEARCH_RADIUS_KM * 2, settings.MAX_SEARCH_RADIUS_KM]
    next_radius = next((s for s in expansion_steps if s > current_radius), None)

    if next_radius is None:
        request.request_status = "failed"
        db.commit()
        logger.info(f"[AutoExpand] Max radius reached — request {request_id} failed")
        return

    logger.info(f"[AutoExpand] Expanding radius {current_radius}km → {next_radius}km for request {request_id}")

    all_candidates = MatchingAgent(db).run(request, radius_km=next_radius)
    new_candidates = [c for c in all_candidates if str(c["donor"].donor_id) not in already_called_ids]

    if not new_candidates:
        request.request_status = "failed"
        db.commit()
        logger.info(f"[AutoExpand] No new donors at {next_radius}km — request {request_id} failed")
        return

    eligible, ineligible = EligibilityAgent(db).run(new_candidates)
    if not eligible:
        request.request_status = "failed"
        db.commit()
        return

    request.search_radius_km = next_radius
    request.expansion_count = (request.expansion_count or 0) + 1
    request.request_status = "in_progress"
    db.commit()

    call_agent = CallAssistantAgent(db, TwilioService(), SMSService())
    call_agent.create_call_records(request, eligible[:5], ineligible)

    top_5 = (
        db.query(CallResponse)
        .filter(CallResponse.request_id == request_id, CallResponse.call_status == "pending")
        .order_by(CallResponse.rank_position)
        .limit(5)
        .all()
    )
    for record in top_5:
        call_agent.initiate_call(request, record)

    logger.info(f"[AutoExpand] Called {len(top_5)} new donors at {next_radius}km (expansion #{request.expansion_count})")


