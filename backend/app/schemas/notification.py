from datetime import datetime

from pydantic import BaseModel, Field


class QQGroupBindingRead(BaseModel):
    id: str
    binding_code: str
    group_openid: str | None
    enabled: bool
    daily_summary_time: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class QQGroupBindingUpdate(BaseModel):
    enabled: bool | None = None
    daily_summary_time: str | None = Field(default=None, pattern=r"^\d{2}:\d{2}$")


class QQGroupManualBind(BaseModel):
    group_openid: str = Field(min_length=1, max_length=160)


class TestNotificationResponse(BaseModel):
    status: str
    detail: str
