from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class CallResponseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    call_response_id: UUID
    request_id: UUID
    donor_id: UUID
    call_status: str
    eta_minutes: Optional[int] = None
    fit_to_donate_today: Optional[bool] = None
    medication_response: Optional[str] = None
    location_consent: bool
    map_sent: bool
    ineligibility_reason: Optional[str] = None
    rank_position: Optional[int] = None
    response_timestamp: Optional[datetime] = None
    created_at: datetime


class CallWebhookPayload(BaseModel):
    CallSid: str
    CallStatus: str
    From: Optional[str] = None
    To: Optional[str] = None
    SpeechResult: Optional[str] = None
    Digits: Optional[str] = None


class LocationConsentPayload(BaseModel):
    token: str
    latitude: float
    longitude: float


class ManualOverridePayload(BaseModel):
    donor_id: UUID
    call_status: str
    eta_minutes: Optional[int] = None
    notes: Optional[str] = None
