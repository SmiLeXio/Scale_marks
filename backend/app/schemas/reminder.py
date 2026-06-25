from datetime import datetime

from pydantic import BaseModel, Field


class ReminderBase(BaseModel):
    pet_id: str
    type: str = Field(min_length=1, max_length=40)
    title: str = Field(min_length=1, max_length=120)
    description: str | None = None
    due_date: datetime
    repeat_type: str = Field(default="once", max_length=30)
    repeat_interval_days: int | None = Field(default=None, ge=1, le=365)


class ReminderCreate(ReminderBase):
    pass


class ReminderRead(ReminderBase):
    id: str
    is_completed: bool
    completed_at: datetime | None
    created_at: datetime
    pet_name: str | None = None

    model_config = {"from_attributes": True}
