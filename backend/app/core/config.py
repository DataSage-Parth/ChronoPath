"""
Backend configuration — loaded from environment variables or .env file.
"""

from pydantic_settings import BaseSettings
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

    class Config:
        env_file = ".env"


settings = Settings()
