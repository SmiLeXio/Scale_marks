from datetime import date, datetime

from pydantic import BaseModel, Field


class FeedingRecordBase(BaseModel):
    date: date
    food_type: str = Field(min_length=1, max_length=80)
    food_weight: float | None = Field(default=None, ge=0)
    is_success: bool = True
    refused: bool = False
    note: str | None = None


class FeedingRecordCreate(FeedingRecordBase):
    pass


class FeedingRecordRead(FeedingRecordBase):
    id: str
    pet_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedingSuggestion(BaseModel):
    pet_id: str
    species: str
    weight: float
    suggested_amount: float
    feeding_cycle_days: int
    calcium_cycle_days: int
    next_feeding_date: date | None
