from datetime import timedelta

from fastapi import APIRouter, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.api.pets import get_owned_pet
from app.models.feeding import FeedingRecord
from app.models.reminder import Reminder
from app.schemas.feeding import FeedingRecordCreate, FeedingRecordRead, FeedingSuggestion
from app.services.feeding import (
    calculate_calcium_cycle,
    calculate_feeding_amount,
    calculate_feeding_cycle,
    calculate_next_feeding_date,
)

router = APIRouter(prefix="/pets/{pet_id}/feeding", tags=["feeding"])


@router.get("", response_model=list[FeedingRecordRead])
def list_feeding_records(pet_id: str, current_user: CurrentUser, db: DbSession) -> list[FeedingRecord]:
    get_owned_pet(db, pet_id, current_user.id)
    return list(
        db.scalars(
            select(FeedingRecord)
            .where(FeedingRecord.pet_id == pet_id)
            .order_by(FeedingRecord.date.desc())
        )
    )


@router.post("", response_model=FeedingRecordRead, status_code=status.HTTP_201_CREATED)
def create_feeding_record(
    pet_id: str,
    payload: FeedingRecordCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> FeedingRecord:
    pet = get_owned_pet(db, pet_id, current_user.id)
    record = FeedingRecord(**payload.model_dump(), pet_id=pet_id)
    pet.last_feeding_date = payload.date

    due_date = payload.date + timedelta(days=pet.feeding_cycle)
    reminder = Reminder(
        pet_id=pet_id,
        type="feeding",
        title=f"{pet.name} 下次喂食",
        description="由喂食记录自动生成",
        due_date=due_date,
        repeat_type="once",
    )
    db.add(record)
    db.add(reminder)
    db.commit()
    db.refresh(record)
    return record


@router.get("/calculate", response_model=FeedingSuggestion)
def calculate_feeding(pet_id: str, current_user: CurrentUser, db: DbSession) -> FeedingSuggestion:
    pet = get_owned_pet(db, pet_id, current_user.id)
    weight = pet.weight or 0
    cycle = calculate_feeding_cycle(weight) if weight else pet.feeding_cycle
    return FeedingSuggestion(
        pet_id=pet.id,
        species=pet.species,
        weight=weight,
        suggested_amount=calculate_feeding_amount(pet.species, weight) if weight else 0,
        feeding_cycle_days=cycle,
        calcium_cycle_days=calculate_calcium_cycle(False),
        next_feeding_date=calculate_next_feeding_date(pet.last_feeding_date, pet.feeding_cycle),
    )
