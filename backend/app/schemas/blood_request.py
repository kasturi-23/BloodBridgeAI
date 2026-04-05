from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class BloodRequestCreate(BaseModel):
    hospital_name: str
    hospital_location: str
    hospital_latitude: float
    hospital_longitude: float
    contact_person: str
    blood_type_needed: str
    units_required: int = Field(ge=1, le=20)
    urgency_level: Literal["Low", "Medium", "High", "Critical"]
    required_within_hours: int = Field(ge=1, le=72)
    notes: str | None = None


class BloodRequestOut(BloodRequestCreate):
    model_config = ConfigDict(populate_by_name=True)

    request_id: str
    status: Literal["pending", "fulfilled", "in_progress"] = "pending"
    created_at: datetime


class MatchSummaryOut(BaseModel):
    request: BloodRequestOut
    total_matches: int
    top_matches: list
    ai_summary: str
