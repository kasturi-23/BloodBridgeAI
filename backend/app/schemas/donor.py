<<<<<<< HEAD
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class DonorCreate(BaseModel):
    full_name: str
    phone_number: str
    blood_group: str
    age: Optional[int] = None
    weight: Optional[float] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    last_donation_date: Optional[datetime] = None
    screening_status: str = "cleared"
    medication_flag: bool = False
    temporary_deferral_flag: bool = False
    availability_status: str = "available"


class DonorUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    blood_group: Optional[str] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    last_donation_date: Optional[datetime] = None
    screening_status: Optional[str] = None
    medication_flag: Optional[bool] = None
    temporary_deferral_flag: Optional[bool] = None
    availability_status: Optional[str] = None
    is_active: Optional[bool] = None


class DonorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    donor_id: UUID
    full_name: str
    phone_number: str
    blood_group: str
    age: Optional[int] = None
    weight: Optional[float] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    last_donation_date: Optional[datetime] = None
    screening_status: str
    medication_flag: bool
    temporary_deferral_flag: bool
    availability_status: str
    past_response_score: float
    is_active: bool
    created_at: datetime


class DonorSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    donor_id: UUID
    full_name: str
    blood_group: str
    distance_km: Optional[float] = None
    eta_minutes: Optional[int] = None
    call_status: Optional[str] = None
    rank_position: Optional[int] = None
    past_response_score: float
=======
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class DonorBase(BaseModel):
    full_name: str
    age: int = Field(ge=18, le=65)
    gender: str
    blood_group: str
    city: str
    latitude: float
    longitude: float
    phone: str
    email: EmailStr
    last_donation_date: datetime
    health_screening_status: Literal["passed", "pending", "failed"]
    eligibility_status: Literal["eligible", "ineligible"]
    availability_status: Literal["available", "unavailable", "busy"]
    past_response_rate: float = Field(ge=0, le=1)
    total_donations: int = Field(ge=0)
    preferred_contact_method: Literal["sms", "email"] = "sms"
    notes: str | None = None


class DonorCreate(DonorBase):
    donor_id: str


class DonorUpdate(BaseModel):
    availability_status: Literal["available", "unavailable", "busy"] | None = None
    eligibility_status: Literal["eligible", "ineligible"] | None = None
    health_screening_status: Literal["passed", "pending", "failed"] | None = None
    contacted: bool | None = None
    responded: bool | None = None
    notes: str | None = None


class DonorOut(DonorBase):
    model_config = ConfigDict(populate_by_name=True)

    donor_id: str
    contacted: bool = False
    responded: bool = False
    created_at: datetime


class DonorMatchOut(BaseModel):
    donor_id: str
    full_name: str
    blood_group: str
    city: str
    distance_miles: float
    eligibility_status: str
    availability_status: str
    response_probability: float
    ranking_score: float
    recommendation_tag: str
>>>>>>> a3f81144c587ef50313ffd6654e433970229adef
