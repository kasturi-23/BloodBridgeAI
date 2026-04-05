from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import logging

from app.database import get_db
from app.models.hospital_request import HospitalRequest
from app.models.call_response import CallResponse
from app.schemas.hospital_request import RequestCreate, RequestOut, RequestStatus
from app.agents.matching_agent import MatchingAgent
from app.agents.eligibility_agent import EligibilityAgent
from app.agents.call_assistant_agent import CallAssistantAgent
from app.services.twilio_service import TwilioService
from app.services.sms_service import SMSService
from app.config import settings

router = APIRouter(prefix="/api/requests", tags=["requests"])
logger = logging.getLogger(__name__)


def run_matching_pipeline(request_id: str, db: Session):
    """Background task: run matching + eligibility + create call records."""
    try:
        request = db.query(HospitalRequest).filter(
            HospitalRequest.request_id == request_id
        ).first()
        if not request:
            return

        request.request_status = "in_progress"
        db.commit()

        # Agent 1: Matching
        matching_agent = MatchingAgent(db)
        shortlisted = matching_agent.run(request)

        if not shortlisted:
            shortlisted = matching_agent.expand_radius_and_run(request)

        if not shortlisted:
            logger.warning(f"No compatible donors found for request {request_id}")
            request.request_status = "failed"
            db.commit()
            return

        # Agent 2: Eligibility
        eligibility_agent = EligibilityAgent(db)
        eligible, ineligible = eligibility_agent.run(shortlisted)

        if not eligible:
            logger.warning(f"No eligible donors for request {request_id}")
            request.request_status = "failed"
            db.commit()
            return

        # Store ranked donor IDs on the request
        request.ranked_donor_ids = [
            str(item["donor"].donor_id) for item in eligible
        ]
        db.commit()

        # Agent 3: Create call records
        twilio_svc = TwilioService()
        sms_svc = SMSService()
        call_agent = CallAssistantAgent(db, twilio_service=twilio_svc, sms_service=sms_svc)
        call_agent.create_call_records(request, eligible, ineligible)

        # Initiate calls to top 5 donors simultaneously
        top_5 = (
            db.query(CallResponse)
            .filter(
                CallResponse.request_id == request.request_id,
                CallResponse.call_status == "pending",
            )
            .order_by(CallResponse.rank_position)
            .limit(5)
            .all()
        )
        for record in top_5:
            call_agent.initiate_call(request, record)

        logger.info(f"Matching pipeline complete for request {request_id}")

    except Exception as e:
        logger.error(f"Error in matching pipeline for {request_id}: {e}", exc_info=True)


@router.post("/", response_model=RequestOut, status_code=201)
def create_request(
    payload: RequestCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Create a new hospital blood request and trigger the matching pipeline."""
    request = HospitalRequest(
        hospital_name=settings.HOSPITAL_NAME,
        hospital_address=settings.HOSPITAL_ADDRESS,
        hospital_latitude=settings.HOSPITAL_LAT,
        hospital_longitude=settings.HOSPITAL_LNG,
        blood_group_needed=payload.blood_group_needed.upper(),
        units_needed=payload.units_needed,
        urgency_level=payload.urgency_level,
        required_by_time=payload.required_by_time,
        notes=payload.notes,
        created_by=payload.created_by,
        request_status="open",
    )
    db.add(request)
    db.commit()
    db.refresh(request)

    # Run matching pipeline asynchronously
    background_tasks.add_task(run_matching_pipeline, str(request.request_id), db)

    logger.info(f"New blood request created: {request.request_id} for {payload.blood_group_needed}")
    return request


@router.get("/", response_model=List[RequestOut])
def list_requests(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return (
        db.query(HospitalRequest)
        .order_by(HospitalRequest.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{request_id}", response_model=RequestOut)
def get_request(request_id: UUID, db: Session = Depends(get_db)):
    request = db.query(HospitalRequest).filter(
        HospitalRequest.request_id == request_id
    ).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request


@router.patch("/{request_id}/status", response_model=RequestOut)
def update_request_status(
    request_id: UUID,
    payload: RequestStatus,
    db: Session = Depends(get_db),
):
    """Manual status override by hospital staff."""
    request = db.query(HospitalRequest).filter(
        HospitalRequest.request_id == request_id
    ).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    allowed = {"open", "in_progress", "donor_confirmed", "closed", "failed"}
    if payload.request_status not in allowed:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {allowed}")

    request.request_status = payload.request_status
    db.commit()
    db.refresh(request)
    return request


@router.post("/{request_id}/match", status_code=202)
def trigger_match(
    request_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Manually re-trigger the matching pipeline for a request."""
    request = db.query(HospitalRequest).filter(
        HospitalRequest.request_id == request_id
    ).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    background_tasks.add_task(run_matching_pipeline, str(request_id), db)
    return {"message": "Matching pipeline triggered", "request_id": str(request_id)}
