"""
Backend configuration — loaded from environment variables or .env file.
"""

import json
from pydantic_settings import BaseSettings
from pydantic import field_validator
from pathlib import Path
from typing import List


class Settings(BaseSettings):
    """App settings — override via env vars or .env file."""
    APP_NAME: str = "ChronoPath"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    MODEL_DIR: Path = Path(__file__).resolve().parent.parent.parent / "models"

    # AI Career Coach (optional — set OPENAI_API_KEY in .env)
    OPENAI_API_KEY: str = ""
    COACH_MODEL: str = "gpt-4o-mini"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Accept comma-separated string, JSON array, or Python list."""
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                return json.loads(v)
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    class Config:
        env_file = ".env"


settings = Settings()
