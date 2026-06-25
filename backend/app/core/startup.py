from app import models  # noqa: F401
from app.core.database import Base, engine


def ensure_sqlite_columns() -> None:
    if not str(engine.url).startswith("sqlite"):
        return

    with engine.begin() as conn:
        reminder_columns = {
            row[1] for row in conn.exec_driver_sql("PRAGMA table_info(reminders)").fetchall()
        }
        if "repeat_interval_days" not in reminder_columns:
            conn.exec_driver_sql("ALTER TABLE reminders ADD COLUMN repeat_interval_days INTEGER")


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_sqlite_columns()
