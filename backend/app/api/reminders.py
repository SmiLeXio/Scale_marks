from datetime import datetime, time

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api.deps import CurrentUser, DbSession
from app.api.pets import get_owned_pet
from app.models.pet import Pet
from app.models.reminder import Reminder
from app.schemas.reminder import ReminderCreate, ReminderRead
from app.services.reminder_schedule import next_due_date

router = APIRouter(prefix="/reminders", tags=["reminders"])


def serialize_reminder(reminder: Reminder) -> ReminderRead:
    return ReminderRead(
        id=reminder.id,
        pet_id=reminder.pet_id,
        pet_name=reminder.pet.name if reminder.pet else None,
        type=reminder.type,
        title=reminder.title,
        description=reminder.description,
        due_date=reminder.due_date,
        repeat_type=reminder.repeat_type,
        repeat_interval_days=reminder.repeat_interval_days,
        is_completed=reminder.is_completed,
        completed_at=reminder.completed_at,
        created_at=reminder.created_at,
    )


def user_reminder_query(user_id: str):
    return (
        select(Reminder)
        .join(Pet)
        .options(joinedload(Reminder.pet))
        .where(Pet.user_id == user_id)
        .order_by(Reminder.due_date.asc())
    )


@router.get("", response_model=list[ReminderRead])
def list_reminders(current_user: CurrentUser, db: DbSession) -> list[ReminderRead]:
    reminders = db.scalars(user_reminder_query(current_user.id)).unique().all()
    return [serialize_reminder(reminder) for reminder in reminders]


@router.get("/today", response_model=list[ReminderRead])
def today_reminders(current_user: CurrentUser, db: DbSession) -> list[ReminderRead]:
    now = datetime.now()
    start = datetime.combine(now.date(), time.min)
    end = datetime.combine(now.date(), time.max)
    query = user_reminder_query(current_user.id).where(
        Reminder.due_date >= start,
        Reminder.due_date <= end,
        Reminder.is_completed.is_(False),
    )
    reminders = db.scalars(query).unique().all()
    return [serialize_reminder(reminder) for reminder in reminders]


@router.post("", response_model=ReminderRead, status_code=status.HTTP_201_CREATED)
def create_reminder(
    payload: ReminderCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> ReminderRead:
    get_owned_pet(db, payload.pet_id, current_user.id)
    reminder = Reminder(**payload.model_dump())
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    reminder = db.scalar(
        select(Reminder).options(joinedload(Reminder.pet)).where(Reminder.id == reminder.id)
    )
    return serialize_reminder(reminder)


@router.put("/{reminder_id}/complete", response_model=ReminderRead)
def complete_reminder(
    reminder_id: str,
    current_user: CurrentUser,
    db: DbSession,
) -> ReminderRead:
    reminder = db.scalar(user_reminder_query(current_user.id).where(Reminder.id == reminder_id))
    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    reminder.completed_at = datetime.utcnow()
    next_date = next_due_date(reminder)
    if next_date:
        reminder.due_date = next_date
        reminder.is_completed = False
    else:
        reminder.is_completed = True
    db.commit()
    db.refresh(reminder)
    return serialize_reminder(reminder)
