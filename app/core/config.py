from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Settings for Org Structure API app."""

    app_name: str = "Org Structure API"
    app_description: str = "API for org structure management"

    database_url: str = "postgresql://postgres_user:postgres_password@localhost:5432/blog_db"
    redis_url: str = "redis://localhost:6379/0"
    test_redis_url: str = "redis://localhost:6379/1"

    cache_ttl: int = 3600  # время жизни кеша

    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), extra="ignore")


settings = Settings()  # type: ignore