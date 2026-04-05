import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Donor(Base):
    __tablename__ = "donors"

    donor_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(200), nullable=False)
    phone_number = Column(String(20), nullable=False, unique=True)
    blood_group = Column(String(5), nullable=False)  # A+, A-, B+, B-, AB+, AB-, O+, O-
    date_of_birth = Column(DateTime, nullable=True)
    age = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)  # kg
    address = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Eligibility fields
    last_donation_date = Column(DateTime, nullable=True)
    screening_status = Column(String(20), default="cleared")  # cleared, pending, failed
    medication_flag = Column(Boolean, default=False)
    temporary_deferral_flag = Column(Boolean, default=False)
    temporary_deferral_until = Column(DateTime, nullable=True)
    health_notes = Column(Text, nullable=True)

    # Operational fields
    availability_status = Column(String(20), default="available")  # available, unavailable, on_call
    consent_to_location_share = Column(Boolean, default=False)
    past_response_score = Column(Float, default=0.5)  # 0-1, likelihood of responding

    # Meta
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    call_responses = relationship("CallResponse", back_populates="donor")
