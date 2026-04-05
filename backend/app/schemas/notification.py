from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class NotificationGenerateIn(BaseModel):
    donor_id: str
    request_id: str
    channel: Literal["sms", "email"]


class NotificationSendIn(BaseModel):
    donor_id: str
    request_id: str
    channel: Literal["sms", "email"]
    generated_message: str


class NotificationOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    notification_id: str
    donor_id: str
    request_id: str
    channel: str
    generated_message: str
    sent_status: Literal["sent", "failed", "queued"]
    sent_at: datetime | None = None
