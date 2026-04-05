"""
Call Poller
Periodically polls Bland.ai for completed calls instead of relying on webhooks.
This means no public URL / ngrok is needed.
"""
import asyncio
import logging
from datetime import datetime

from app.database import SessionLocal
from app.models.call_response import CallResponse
from app.models.hospital_request import HospitalRequest
from app.services.twilio_service import TwilioService
from app.services.sms_service import SMSService
from app.services.transcript_analysis_service import TranscriptAnalysisService
from app.agents.call_assistant_agent import CallAssistantAgent

logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 15


async def poll_active_calls():
    """Background loop: check all 'calling' records against Bland.ai every 15s."""
    twilio_svc = TwilioService()
    analysis_svc = TranscriptAnalysisService()

    while True:
        await asyncio.sleep(POLL_INTERVAL_SECONDS)
        try:
            _check_calls(twilio_svc, analysis_svc)
        except Exception as e:
            logger.error(f"[CallPoller] Unexpected error: {e}", exc_info=True)


def _check_calls(twilio_svc: TwilioService, analysis_svc: TranscriptAnalysisService):
    db = SessionLocal()
    try:
        calling_records = (
            db.query(CallResponse)
            .filter(CallResponse.call_status == "calling")
            .all()
        )

        if not calling_records:
            return

        logger.info(f"[CallPoller] Checking {len(calling_records)} active call(s)")

        for record in calling_records:
            if not record.twilio_call_sid:
                continue

            result = twilio_svc.get_call_result(record.twilio_call_sid)
            if result is None:
                continue  # still in progress

            logger.info(
                f"[CallPoller] Call {record.twilio_call_sid} done — "
                f"status={result['status']}, answered_by={result['answered_by']}"
            )

            request = db.query(HospitalRequest).filter(
                HospitalRequest.request_id == record.request_id
            ).first()

            agent = CallAssistantAgent(db, twilio_svc, SMSService())

            # No-answer / voicemail / failed
            if result["status"] in ("no-answer", "busy", "failed") or result["answered_by"] == "voicemail":
                agent.process_no_answer(record)
                _call_next_donor(record.request_id, db, twilio_svc)
                continue

            # GPT analyzes the transcript
            analysis = analysis_svc.analyze(result["transcript"], result["summary"])
            logger.info(f"[CallPoller] GPT decision for donor {record.donor_id}: {analysis}")

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
                logger.info(f"[CallPoller] Donor {record.donor_id} ACCEPTED — ETA {eta_minutes} min")

            elif accepted is False:
                agent.process_declination(record, reason=decline_reason or "Donor declined")
                _call_next_donor(record.request_id, db, twilio_svc)
                logger.info(f"[CallPoller] Donor {record.donor_id} DECLINED — {decline_reason}")

            else:
                record.call_status = "call_ended"
                record.response_timestamp = datetime.utcnow()
                db.commit()
                _call_next_donor(record.request_id, db, twilio_svc)
                logger.info(f"[CallPoller] Donor {record.donor_id} — call ended, no clear answer")

    finally:
        db.close()


def _call_next_donor(request_id, db, twilio_svc):
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
        return  # other calls still ongoing

    has_accepted = db.query(CallResponse).filter(
        CallResponse.request_id == request_id,
        CallResponse.call_status == "accepted",
    ).first()
    if has_accepted:
        return  # already confirmed

    # All current donors exhausted — try expanding radius
    already_called_ids = [
        str(r.donor_id) for r in db.query(CallResponse)
        .filter(CallResponse.request_id == request_id).all()
    ]

    current_radius = request.search_radius_km or settings.DEFAULT_SEARCH_RADIUS_KM
    expansion_steps = [
        settings.DEFAULT_SEARCH_RADIUS_KM * 2,
        settings.MAX_SEARCH_RADIUS_KM,
    ]

    next_radius = None
    for step in expansion_steps:
        if step > current_radius:
            next_radius = step
            break

    if next_radius is None:
        # Exhausted all radii — mark failed
        request.request_status = "failed"
        db.commit()
        logger.info(f"[AutoExpand] Max radius reached, no donors found — request {request_id} failed")
        return

    logger.info(
        f"[AutoExpand] All donors declined for request {request_id}. "
        f"Expanding radius {current_radius}km → {next_radius}km"
    )

    # Find new donors at expanded radius, excluding already-called ones
    matching_agent = MatchingAgent(db)
    all_candidates = matching_agent.run(request, radius_km=next_radius)
    new_candidates = [c for c in all_candidates if str(c["donor"].donor_id) not in already_called_ids]

    if not new_candidates:
        request.request_status = "failed"
        db.commit()
        logger.info(f"[AutoExpand] No new donors at {next_radius}km — request {request_id} failed")
        return

    eligibility_agent = EligibilityAgent(db)
    eligible, ineligible = eligibility_agent.run(new_candidates)

    if not eligible:
        request.request_status = "failed"
        db.commit()
        logger.info(f"[AutoExpand] No eligible donors at {next_radius}km — request {request_id} failed")
        return

    # Update radius tracking
    request.search_radius_km = next_radius
    request.expansion_count = (request.expansion_count or 0) + 1
    request.request_status = "in_progress"
    db.commit()

    # Create call records and call top 5
    call_agent = CallAssistantAgent(db, twilio_svc, SMSService())
    call_agent.create_call_records(request, eligible[:5], ineligible)

    top_5 = (
        db.query(CallResponse)
        .filter(
            CallResponse.request_id == request_id,
            CallResponse.call_status == "pending",
        )
        .order_by(CallResponse.rank_position)
        .limit(5)
        .all()
    )

    for record in top_5:
        call_agent.initiate_call(request, record)

    logger.info(
        f"[AutoExpand] Calling {len(top_5)} new donors at {next_radius}km "
        f"(expansion #{request.expansion_count})"
    )
