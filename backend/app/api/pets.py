from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.pet import Pet
from app.schemas.pet import PetCreate, PetRead, PetUpdate

router = APIRouter(prefix="/pets", tags=["pets"])


def get_owned_pet(db: DbSession, pet_id: str, user_id: str) -> Pet:
    pet = db.scalar(select(Pet).where(Pet.id == pet_id, Pet.user_id == user_id))
    if not pet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pet not found")
    return pet


@router.get("", response_model=list[PetRead])
def list_pets(current_user: CurrentUser, db: DbSession) -> list[Pet]:
    return list(db.scalars(select(Pet).where(Pet.user_id == current_user.id).order_by(Pet.created_at.desc())))


@router.post("", response_model=PetRead, status_code=status.HTTP_201_CREATED)
def create_pet(payload: PetCreate, current_user: CurrentUser, db: DbSession) -> Pet:
    pet = Pet(**payload.model_dump(), user_id=current_user.id)
    db.add(pet)
    db.commit()
    db.refresh(pet)
    return pet


@router.get("/{pet_id}", response_model=PetRead)
def read_pet(pet_id: str, current_user: CurrentUser, db: DbSession) -> Pet:
    return get_owned_pet(db, pet_id, current_user.id)


@router.put("/{pet_id}", response_model=PetRead)
def update_pet(pet_id: str, payload: PetUpdate, current_user: CurrentUser, db: DbSession) -> Pet:
    pet = get_owned_pet(db, pet_id, current_user.id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(pet, key, value)
    db.commit()
    db.refresh(pet)
    return pet


@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet(pet_id: str, current_user: CurrentUser, db: DbSession) -> None:
    pet = get_owned_pet(db, pet_id, current_user.id)
    db.delete(pet)
    db.commit()
