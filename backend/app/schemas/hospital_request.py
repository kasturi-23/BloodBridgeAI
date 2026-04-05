from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class RequestCreate(BaseModel):
    blood_group_needed: str
    units_needed: int = 1
    urgency_level: str = "high"
    required_by_time: Optional[datetime] = None
    notes: Optional[str] = None
    created_by: Optional[str] = None


class RequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    request_id: UUID
    hospital_name: str
    hospital_address: str
    blood_group_needed: str
    units_needed: int
    units_confirmed: int
    urgency_level: str
    required_by_time: Optional[datetime] = None
    notes: Optional[str] = None
    request_status: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class RequestStatus(BaseModel):
    request_status: str


class DashboardDonorCard(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    call_response_id: Optional[UUID] = None
    donor_id: UUID
    full_name: str
    blood_group: str
    phone_number: str
    distance_km: Optional[float] = None
    call_status: str
    eta_minutes: Optional[int] = None
    fit_to_donate_today: Optional[bool] = None
    map_sent: bool
    location_consent: bool
    rank_position: Optional[int] = None
    ineligibility_reason: Optional[str] = None
    response_timestamp: Optional[datetime] = None


class DashboardPayload(BaseModel):
    request: RequestOut
    confirmed_donors: List[DashboardDonorCard]
    standby_donors: List[DashboardDonorCard]
    pending_donors: List[DashboardDonorCard]
    declined_donors: List[DashboardDonorCard]
    total_donors_contacted: int
