"""
Call Assistant Agent
Responsibility: Contact donors, collect real-time responses, store ETA, deliver directions.
Inputs: Eligible ranked donors, hospital details, call script, SMS templates.
Outputs: Accepted/declined status, ETA, consent flags, map sent status.
"""
import uuid
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.donor import Donor
from app.models.hospital_request import HospitalRequest
from app.models.call_response import CallResponse
from app.config import settings

logger = logging.getLogger(__name__)

# Configurable voice script (not hard-coded in frontend)
CALL_SCRIPT = {
    "greeting": (
        "Hello, this is the BloodBridge emergency donation assistant "
        "calling on behalf of {hospital_name}."
    ),
    "reason": (
        "A patient urgently requires {blood_group} blood. "
        "Are you available to come to the hospital immediately?"
    ),
    "eta_question": (
        "Thank you. Approximately how many minutes will it take you to reach the hospital?"
    ),
    "health_check": "Are you feeling healthy and fit to donate today?",
    "medication_check": (
        "Have you taken any medication recently that may affect donation eligibility?"
    ),
    "location_consent": (
        "Would you like to share your current location through a secure link "
        "so the hospital can estimate your arrival time?"
    ),
    "close": (
        "Thank you. Your response has been recorded. "
        "I am now sending you the hospital address and directions by message."
    ),
    "decline_close": (
        "Thank you for your time. We will reach out to another donor. "
        "We appreciate your willingness to help."
    ),
}


class CallAssistantAgent:
    """
    Agent 3: Orchestrate donor outreach calls and record outcomes.
    Works with Twilio service for actual telephony.
    """

    def __init__(self, db: Session, twilio_service=None, sms_service=None):
        self.db = db
        self.twilio_service = twilio_service
        self.sms_service = sms_service

    def get_script(self, step: str, **kwargs) -> str:
        template = CALL_SCRIPT.get(step, "")
        return template.format(**kwargs)

    def create_call_records(
        self,
        request: HospitalRequest,
        eligible_donors: List[Dict[str, Any]],
        ineligible_donors: List[Dict[str, Any]],
    ) -> List[CallResponse]:
        """
        Create CallResponse records for all donors (eligible + ineligible).
        Ineligible donors are pre-filled with rejection reasons.
        """
        records = []

        # Eligible donors — create as pending
        for rank, item in enumerate(eligible_donors, start=1):
            donor: Donor = item["donor"]
            existing = (
                self.db.query(CallResponse)
                .filter(
                    CallResponse.request_id == request.request_id,
                    CallResponse.donor_id == donor.donor_id,
                )
                .first()
            )
            if existing:
                records.append(existing)
                continue

            record = CallResponse(
                request_id=request.request_id,
                donor_id=donor.donor_id,
                call_status="pending",
                rank_position=rank,
            )
            self.db.add(record)
            records.append(record)

        # Ineligible donors — pre-fill with reason
        for item in ineligible_donors:
            donor: Donor = item["donor"]
            existing = (
                self.db.query(CallResponse)
                .filter(
                    CallResponse.request_id == request.request_id,
                    CallResponse.donor_id == donor.donor_id,
                )
                .first()
            )
            if existing:
                continue

            record = CallResponse(
                request_id=request.request_id,
                donor_id=donor.donor_id,
                call_status="ineligible",
                ineligibility_reason=item.get("rejection_reason", "Ineligible"),
                rank_position=None,
            )
            self.db.add(record)

        self.db.commit()
        return records

    def initiate_call(self, request: HospitalRequest, call_record: CallResponse) -> bool:
        """
        Place an outbound call to the donor via Twilio.
        Returns True if call was initiated successfully.
        """
        donor = self.db.query(Donor).filter(Donor.donor_id == call_record.donor_id).first()
        if not donor:
            return False

        call_record.call_status = "calling"
        call_record.call_started_at = datetime.utcnow()
        self.db.commit()

        if self.twilio_service:
            try:
                call_sid = self.twilio_service.place_call(
                    to_number=donor.phone_number,
                    request_id=str(request.request_id),
                    call_response_id=str(call_record.call_response_id),
                    hospital_name=request.hospital_name,
                    blood_group=request.blood_group_needed,
                )
                call_record.twilio_call_sid = call_sid
                self.db.commit()
                logger.info(f"[CallAssistantAgent] Call placed to {donor.phone_number}, SID: {call_sid}")
                return True
            except Exception as e:
                logger.error(f"[CallAssistantAgent] Failed to place call: {e}")
                call_record.call_status = "no_answer"
                self.db.commit()
                return False
        else:
            # Dev mode: simulate call
            logger.warning(
                f"[CallAssistantAgent] DEV MODE — Simulating call to {donor.phone_number} "
                f"for donor {donor.full_name}"
            )
            return True

    def process_acceptance(
        self,
        call_record: CallResponse,
        eta_minutes: Optional[int],
        fit_to_donate: bool,
        medication_response: Optional[str],
        location_consent: bool,
    ) -> bool:
        """
        Process a donor's acceptance and send SMS directions.
        Returns True if donor is confirmed and map sent.
        """
        request = self.db.query(HospitalRequest).filter(
            HospitalRequest.request_id == call_record.request_id
        ).first()

        if not request:
            return False

        call_record.call_status = "accepted"
        call_record.eta_minutes = eta_minutes
        call_record.fit_to_donate_today = fit_to_donate
        call_record.medication_response = medication_response
        call_record.location_consent = location_consent
        call_record.response_timestamp = datetime.utcnow()

        # Generate location share token if consent given
        if location_consent:
            call_record.location_share_token = str(uuid.uuid4())

        self.db.commit()

        # Send SMS map link
        self._send_map_sms(call_record, request)

        # Update request status
        self._update_request_after_acceptance(request)

        return True

    def process_declination(self, call_record: CallResponse, reason: Optional[str] = None):
        """Record a donor declination and prepare to move to next donor."""
        call_record.call_status = "declined"
        call_record.donor_notes = reason
        call_record.response_timestamp = datetime.utcnow()
        self.db.commit()
        logger.info(
            f"[CallAssistantAgent] Donor {call_record.donor_id} declined request "
            f"{call_record.request_id}"
        )

    def process_no_answer(self, call_record: CallResponse):
        """Record a no-answer outcome."""
        call_record.call_status = "no_answer"
        call_record.response_timestamp = datetime.utcnow()
        self.db.commit()

    def get_next_pending_donor(self, request_id) -> Optional[CallResponse]:
        """Get the next donor in the queue who hasn't been called yet."""
        return (
            self.db.query(CallResponse)
            .filter(
                CallResponse.request_id == request_id,
                CallResponse.call_status == "pending",
            )
            .order_by(CallResponse.rank_position)
            .first()
        )

    def _send_map_sms(self, call_record: CallResponse, request: HospitalRequest):
        donor = self.db.query(Donor).filter(Donor.donor_id == call_record.donor_id).first()
        if not donor:
            return

        maps_link = (
            f"https://www.google.com/maps/dir/?api=1"
            f"&destination={request.hospital_latitude},{request.hospital_longitude}"
        )

        sms_body = (
            f"BloodBridge Confirmation\n"
            f"Thank you for agreeing to donate! Please proceed to:\n"
            f"{request.hospital_name}\n"
            f"{request.hospital_address}\n\n"
            f"Directions: {maps_link}\n\n"
        )

        if call_record.location_share_token:
            consent_link = (
                f"{settings.APP_BASE_URL}/location/share/{call_record.location_share_token}"
            )
            sms_body += f"Share your location with the hospital: {consent_link}\n"

        if self.sms_service:
            try:
                self.sms_service.send_sms(to=donor.phone_number, body=sms_body)
                call_record.map_sent = True
                call_record.map_sent_at = datetime.utcnow()
                self.db.commit()
                logger.info(f"[CallAssistantAgent] Map SMS sent to {donor.phone_number}")
            except Exception as e:
                logger.error(f"[CallAssistantAgent] Failed to send SMS: {e}")
        else:
            logger.warning(
                f"[CallAssistantAgent] DEV MODE — SMS would be sent to {donor.phone_number}:\n{sms_body}"
            )
            call_record.map_sent = True
            call_record.map_sent_at = datetime.utcnow()
            self.db.commit()

    def _update_request_after_acceptance(self, request: HospitalRequest):
        accepted_count = (
            self.db.query(CallResponse)
            .filter(
                CallResponse.request_id == request.request_id,
                CallResponse.call_status == "accepted",
            )
            .count()
        )
        request.units_confirmed = accepted_count
        if accepted_count >= request.units_needed:
            request.request_status = "donor_confirmed"
        else:
            request.request_status = "in_progress"
        self.db.commit()
