from datetime import date, datetime

from app.models.reminder import Reminder


def repeat_interval_days(reminder: Reminder) -> int | None:
    if reminder.repeat_type == "daily":
        return 1
    if reminder.repeat_type == "weekly":
        return 7
    if reminder.repeat_type == "biweekly":
        return 14
    if reminder.repeat_type == "custom":
        return reminder.repeat_interval_days
    return None


def reminder_occurs_on(reminder: Reminder, target_date: date) -> bool:
    first_date = reminder.due_date.date()
    if reminder.repeat_type == "once":
        return first_date == target_date
    if target_date < first_date:
        return False
    if reminder.repeat_type == "monthly":
        return first_date.day == target_date.day

    interval = repeat_interval_days(reminder)
    if not interval:
        return False
    return (target_date - first_date).days % interval == 0


def build_daily_summary(reminders: list[Reminder], target_date: date | None = None) -> str:
    target_date = target_date or datetime.now().date()
    due_reminders = [
        reminder
        for reminder in reminders
        if not reminder.is_completed and reminder_occurs_on(reminder, target_date)
    ]
    if not due_reminders:
        return ""

    lines = [f"鳞迹提醒\n\n今天有 {len(due_reminders)} 个养护任务："]
    for index, reminder in enumerate(due_reminders, start=1):
        pet_name = reminder.pet.name if reminder.pet else "未命名宠物"
        lines.append(f"\n{index}. {pet_name}\n{reminder.title}")
        if reminder.description:
            lines.append(reminder.description)
        if reminder.repeat_type == "custom" and reminder.repeat_interval_days:
            lines.append(f"循环：每 {reminder.repeat_interval_days} 天")
    return "\n".join(lines)
