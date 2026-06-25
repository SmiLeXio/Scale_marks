from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.api.pets import get_owned_pet
from app.models.growth import GrowthRecord
from app.schemas.growth import GrowthRecordCreate, GrowthRecordRead, GrowthRecordUpdate

router = APIRouter(prefix="/pets/{pet_id}/growth", tags=["growth"])


def get_owned_growth_record(db: DbSession, pet_id: str, record_id: str, user_id: str) -> GrowthRecord:
    get_owned_pet(db, pet_id, user_id)
    record = db.scalar(
        select(GrowthRecord).where(GrowthRecord.id == record_id, GrowthRecord.pet_id == pet_id)
    )
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Growth record not found")
    return record


@router.get("", response_model=list[GrowthRecordRead])
def list_growth_records(pet_id: str, current_user: CurrentUser, db: DbSession) -> list[GrowthRecord]:
    get_owned_pet(db, pet_id, current_user.id)
    return list(
        db.scalars(
            select(GrowthRecord)
            .where(GrowthRecord.pet_id == pet_id)
            .order_by(GrowthRecord.date.asc())
        )
    )


@router.post("", response_model=GrowthRecordRead, status_code=status.HTTP_201_CREATED)
def create_growth_record(
    pet_id: str,
    payload: GrowthRecordCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> GrowthRecord:
    pet = get_owned_pet(db, pet_id, current_user.id)
    record = GrowthRecord(**payload.model_dump(), pet_id=pet_id)
    if payload.weight is not None:
        pet.weight = payload.weight
    if payload.length is not None:
        pet.length = payload.length
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.put("/{record_id}", response_model=GrowthRecordRead)
def update_growth_record(
    pet_id: str,
    record_id: str,
    payload: GrowthRecordUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> GrowthRecord:
    record = get_owned_growth_record(db, pet_id, record_id, current_user.id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_growth_record(
    pet_id: str,
    record_id: str,
    current_user: CurrentUser,
    db: DbSession,
) -> None:
    record = get_owned_growth_record(db, pet_id, record_id, current_user.id)
    db.delete(record)
    db.commit()
