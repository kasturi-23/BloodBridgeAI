import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class HospitalRequest(Base):
    __tablename__ = "hospital_requests"

    request_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hospital_name = Column(String(200), nullable=False)
    hospital_address = Column(Text, nullable=False)
    hospital_latitude = Column(Float, nullable=False)
    hospital_longitude = Column(Float, nullable=False)

    # Blood requirement
    blood_group_needed = Column(String(5), nullable=False)
    units_needed = Column(Integer, nullable=False, default=1)
    units_confirmed = Column(Integer, default=0)
    urgency_level = Column(String(20), nullable=False, default="high")  # low, medium, high, critical
    required_by_time = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    # Status lifecycle: open -> in_progress -> donor_confirmed -> closed / failed
    request_status = Column(String(30), default="open")

    # Ranked donor snapshot (list of donor IDs in order)
    ranked_donor_ids = Column(JSON, default=list)

    # Auto-expand search radius tracking
    search_radius_km = Column(Float, default=None, nullable=True)
    expansion_count = Column(Integer, default=0)

    # Staff info
    created_by = Column(String(200), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

    # Relationships
    call_responses = relationship("CallResponse", back_populates="request")
