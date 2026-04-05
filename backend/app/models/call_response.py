import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class CallResponse(Base):
    __tablename__ = "call_responses"

    call_response_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(UUID(as_uuid=True), ForeignKey("hospital_requests.request_id"), nullable=False)
    donor_id = Column(UUID(as_uuid=True), ForeignKey("donors.donor_id"), nullable=False)

    # Call outcome
    # pending, calling, answered, declined, no_answer, accepted, manual_review
    call_status = Column(String(30), default="pending")
    twilio_call_sid = Column(String(100), nullable=True)

    # Structured call data
    eta_minutes = Column(Integer, nullable=True)
    fit_to_donate_today = Column(Boolean, nullable=True)
    medication_response = Column(Text, nullable=True)
    donor_notes = Column(Text, nullable=True)

    # Location
    location_consent = Column(Boolean, default=False)
    location_share_token = Column(String(200), nullable=True)
    donor_latitude = Column(Float, nullable=True)
    donor_longitude = Column(Float, nullable=True)

    # Delivery
    map_sent = Column(Boolean, default=False)
    map_sent_at = Column(DateTime, nullable=True)

    # Ineligibility reason if filtered
    ineligibility_reason = Column(Text, nullable=True)

    # Priority rank in the outreach queue
    rank_position = Column(Integer, nullable=True)

    response_timestamp = Column(DateTime, nullable=True)
    call_started_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    request = relationship("HospitalRequest", back_populates="call_responses")
    donor = relationship("Donor", back_populates="call_responses")
