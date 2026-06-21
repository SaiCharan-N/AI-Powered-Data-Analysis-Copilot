from functools import lru_cache
from pathlib import Path

import json

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Data Analysis Copilot API"
    app_version: str = "1.0.0"
    environment: str = "development"
    database_url: str = "sqlite:///./data/copilot.db"
    upload_dir: Path = Path("uploads")
    max_upload_mb: int = Field(default=50, ge=1)
    cors_origins: str = (
    "http://localhost:3000,"
    "http://localhost:5173,"
    "http://127.0.0.1:5173"
)
    groq_api_key: str | None = None
    groq_model: str = "llama3-70b-8192"
    sql_generation_max_retries: int = Field(default=3, ge=1, le=5)
    sql_query_timeout_seconds: int = Field(default=10, ge=1, le=120)
    sql_query_max_rows: int = Field(default=10000, ge=1, le=100000)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",

    )

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins.strip().startswith("["):
            parsed = json.loads(self.cors_origins)
            return [str(origin).strip() for origin in parsed if str(origin).strip()]

        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
