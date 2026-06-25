from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "鳞迹 API"
    database_url: str = "sqlite:///./reptilecare.db"
    secret_key: str = "change-me-in-development"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    backend_cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173"
    )
    qq_bot_app_id: str = ""
    qq_bot_secret: str = ""
    qq_bot_sandbox: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
