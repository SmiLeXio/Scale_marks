from datetime import date, datetime

from pydantic import BaseModel, Field


class PetBase(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    species: str = Field(min_length=1, max_length=80)
    morph: str | None = Field(default=None, max_length=120)
    birth_date: date | None = None
    gender: str | None = Field(default=None, max_length=20)
    weight: float | None = Field(default=None, ge=0)
    length: float | None = Field(default=None, ge=0)
    feeding_cycle: int = Field(default=7, ge=1, le=90)
    last_feeding_date: date | None = None
    avatar_url: str | None = None
    notes: str | None = None


class PetCreate(PetBase):
    pass


class PetUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    species: str | None = Field(default=None, min_length=1, max_length=80)
    morph: str | None = Field(default=None, max_length=120)
    birth_date: date | None = None
    gender: str | None = Field(default=None, max_length=20)
    weight: float | None = Field(default=None, ge=0)
    length: float | None = Field(default=None, ge=0)
    feeding_cycle: int | None = Field(default=None, ge=1, le=90)
    last_feeding_date: date | None = None
    avatar_url: str | None = None
    notes: str | None = None


class PetRead(PetBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
