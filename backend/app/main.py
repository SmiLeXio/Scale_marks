from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, feeding, growth, notifications, pets, reminders
from app.core.config import get_settings
from app.core.database import Base, engine
from app import models  # noqa: F401


settings = get_settings()


def ensure_sqlite_columns() -> None:
    if not str(engine.url).startswith("sqlite"):
        return

    with engine.begin() as conn:
        reminder_columns = {
            row[1] for row in conn.exec_driver_sql("PRAGMA table_info(reminders)").fetchall()
        }
        if "repeat_interval_days" not in reminder_columns:
            conn.exec_driver_sql("ALTER TABLE reminders ADD COLUMN repeat_interval_days INTEGER")


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router, prefix="/api")
    app.include_router(pets.router, prefix="/api")
    app.include_router(growth.router, prefix="/api")
    app.include_router(feeding.router, prefix="/api")
    app.include_router(reminders.router, prefix="/api")
    app.include_router(notifications.router, prefix="/api")

    @app.on_event("startup")
    def on_startup() -> None:
        Base.metadata.create_all(bind=engine)
        ensure_sqlite_columns()

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
