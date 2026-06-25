from __future__ import annotations

from datetime import date as date_type
from datetime import datetime

from pydantic import BaseModel, Field


class GrowthRecordBase(BaseModel):
    date: date_type
    weight: float | None = Field(default=None, ge=0)
    length: float | None = Field(default=None, ge=0)
    note: str | None = None


class GrowthRecordCreate(GrowthRecordBase):
    pass


class GrowthRecordUpdate(BaseModel):
    date: date_type | None = None
    weight: float | None = Field(default=None, ge=0)
    length: float | None = Field(default=None, ge=0)
    note: str | None = None


class GrowthRecordRead(GrowthRecordBase):
    id: str
    pet_id: str
    created_at: datetime

    model_config = {"from_attributes": True}
