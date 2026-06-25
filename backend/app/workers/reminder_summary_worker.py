import asyncio
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.database import SessionLocal
from app.core.startup import initialize_database
from app.models.notification import NotificationLog, QQGroupBinding
from app.models.pet import Pet
from app.models.reminder import Reminder
from app.services.qq_notify import QQBotNotifier, QQNotifyError
from app.services.reminder_schedule import build_daily_summary, reminder_occurs_on


POINT_REMINDER_CHANNEL = "qq_group_reminder"
SUMMARY_CHANNEL = "qq_group_summary"


def already_sent_today(db, user_id: str, group_openid: str) -> bool:
    start = datetime.combine(datetime.now().date(), datetime.min.time())
    return bool(
        db.scalar(
            select(NotificationLog).where(
                NotificationLog.user_id == user_id,
                NotificationLog.channel == SUMMARY_CHANNEL,
                NotificationLog.target_id == group_openid,
                NotificationLog.sent_at >= start,
            )
        )
    )


def reminder_occurrence_at(reminder: Reminder, now: datetime) -> datetime | None:
    if not reminder_occurs_on(reminder, now.date()):
        return None
    return datetime.combine(now.date(), reminder.due_date.time()).replace(second=0, microsecond=0)


def reminder_sent_on_date(db, reminder_id: str, group_openid: str, target_date) -> bool:
    start = datetime.combine(target_date, datetime.min.time())
    end = datetime.combine(target_date, datetime.max.time())
    return bool(
        db.scalar(
            select(NotificationLog).where(
                NotificationLog.reminder_id == reminder_id,
                NotificationLog.channel == POINT_REMINDER_CHANNEL,
                NotificationLog.target_id == group_openid,
                NotificationLog.status == "sent",
                NotificationLog.sent_at >= start,
                NotificationLog.sent_at <= end,
            )
        )
    )


def reminder_attempted_recently(db, reminder_id: str, group_openid: str) -> bool:
    recent_cutoff = datetime.utcnow() - timedelta(minutes=10)
    return bool(
        db.scalar(
            select(NotificationLog).where(
                NotificationLog.reminder_id == reminder_id,
                NotificationLog.channel == POINT_REMINDER_CHANNEL,
                NotificationLog.target_id == group_openid,
                NotificationLog.sent_at >= recent_cutoff,
            )
        )
    )


def build_point_reminder_message(reminder: Reminder, occurrence_at: datetime) -> str:
    pet_name = reminder.pet.name if reminder.pet else "未命名宠物"
    lines = [
        "鳞迹提醒",
        "",
        f"{pet_name}：{reminder.title}",
        f"时间：{occurrence_at.strftime('%H:%M')}",
    ]
    if reminder.description:
        lines.append(reminder.description)
    if reminder.repeat_type == "custom" and reminder.repeat_interval_days:
        lines.append(f"循环：每 {reminder.repeat_interval_days} 天")
    return "\n".join(lines)


async def send_due_point_reminders() -> None:
    now = datetime.now().replace(second=0, microsecond=0)
    notifier = QQBotNotifier()

    with SessionLocal() as db:
        bindings = db.scalars(
            select(QQGroupBinding).where(
                QQGroupBinding.enabled.is_(True),
                QQGroupBinding.group_openid.is_not(None),
            )
        ).all()

        for binding in bindings:
            reminders = db.scalars(
                select(Reminder)
                .join(Pet)
                .options(joinedload(Reminder.pet))
                .where(
                    Pet.user_id == binding.user_id,
                    Reminder.is_completed.is_(False),
                )
            ).unique().all()

            for reminder in reminders:
                occurrence_at = reminder_occurrence_at(reminder, now)
                if not occurrence_at or occurrence_at > now:
                    continue
                if reminder_sent_on_date(db, reminder.id, binding.group_openid, occurrence_at.date()):
                    continue
                if reminder_attempted_recently(db, reminder.id, binding.group_openid):
                    continue

                status = "sent"
                error_message = None
                try:
                    await notifier.send_group_message(
                        binding.group_openid,
                        build_point_reminder_message(reminder, occurrence_at),
                    )
                    print(
                        f"[reminder-worker] sent point reminder {reminder.id} to {binding.group_openid}",
                        flush=True,
                    )
                except QQNotifyError as exc:
                    status = "failed"
                    error_message = str(exc)
                    print(
                        f"[reminder-worker] failed point reminder {reminder.id}: {error_message}",
                        flush=True,
                    )

                db.add(
                    NotificationLog(
                        user_id=binding.user_id,
                        reminder_id=reminder.id,
                        channel=POINT_REMINDER_CHANNEL,
                        target_id=binding.group_openid,
                        status=status,
                        error_message=error_message,
                    )
                )
                db.commit()


async def send_due_summaries() -> None:
    now = datetime.now()
    notifier = QQBotNotifier()

    with SessionLocal() as db:
        bindings = db.scalars(
            select(QQGroupBinding).where(
                QQGroupBinding.enabled.is_(True),
                QQGroupBinding.group_openid.is_not(None),
            )
        ).all()

        for binding in bindings:
            if binding.daily_summary_time != now.strftime("%H:%M"):
                continue
            if already_sent_today(db, binding.user_id, binding.group_openid):
                continue

            reminders = db.scalars(
                select(Reminder)
                .join(Pet)
                .options(joinedload(Reminder.pet))
                .where(Pet.user_id == binding.user_id)
            ).unique().all()
            content = build_daily_summary(reminders, now.date())
            if not content:
                continue

            status = "sent"
            error_message = None
            try:
                await notifier.send_group_message(binding.group_openid, content)
            except QQNotifyError as exc:
                status = "failed"
                error_message = str(exc)

            db.add(
                NotificationLog(
                    user_id=binding.user_id,
                    reminder_id=None,
                    channel=SUMMARY_CHANNEL,
                    target_id=binding.group_openid,
                    status=status,
                    error_message=error_message,
                )
            )
            db.commit()


async def main() -> None:
    initialize_database()
    print("[reminder-worker] started", flush=True)
    while True:
        await send_due_point_reminders()
        await send_due_summaries()
        now = datetime.now()
        next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
        await asyncio.sleep(max(1, (next_minute - now).total_seconds()))


if __name__ == "__main__":
    asyncio.run(main())
