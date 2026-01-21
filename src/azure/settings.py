import json
import os
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine which env files to load based on ENV variable
BASE_DIR = Path(__file__).resolve().parent
env = os.getenv("ENV")
env_files = []
if env:
    env_files.append(str(BASE_DIR / f".env.{env}"))
env_files.extend([str(BASE_DIR / ".env.local"), str(BASE_DIR / ".env")])


class Settings(BaseSettings):
    """Application settings loaded from environment files."""

    model_config = SettingsConfigDict(
        env_file=tuple(env_files),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Environment
    environment: str = "local"

    # Logging configuration
    log_level: str = "INFO"

    # Database configuration
    db_host: str
    db_name: str
    db_port: int = 5432
    db_username: str
    db_password: str

    # Azure API configuration
    app_id: str
    api_key: str

    # Top level categories (parsed from JSON string in env)
    top_level_categories: dict[str, int] = {}

    @field_validator("top_level_categories", mode="before")
    @classmethod
    def parse_categories(cls, v):
        """Parse top_level_categories from JSON string if needed."""
        if isinstance(v, str):
            return json.loads(v)
        return v


# Singleton instance
settings = Settings()
