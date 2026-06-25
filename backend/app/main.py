from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, feeding, growth, notifications, pets, reminders
from app.core.config import get_settings
from app.core.startup import initialize_database


settings = get_settings()


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
        initialize_database()

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
