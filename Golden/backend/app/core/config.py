"""Application configuration loaded from environment variables."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Walk up from app/core/config.py to find .env at backend/.env
_backend_dir = Path(__file__).resolve().parent.parent.parent
_env_path = _backend_dir / ".env"
load_dotenv(_env_path)


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default


def _env_origins(default: str) -> list[str]:
    raw = os.getenv("CORS_ORIGINS", default)
    parsed: list[str] = []
    for origin in raw.split(","):
        candidate = origin.strip().rstrip("/")
        if not candidate or candidate == "*":
            continue
        parsed.append(candidate)
    return parsed


class Settings:
    """Central configuration sourced from .env file or environment."""

    APP_ENV: str = os.getenv("APP_ENV", "development").strip().lower()
    IS_PRODUCTION: bool = APP_ENV in {"production", "prod"}
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/tdental"
    )
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    CORS_ORIGINS: list[str] = _env_origins(
        "http://localhost:8899,http://127.0.0.1:8899"
    )
    APP_PORT: int = int(os.getenv("PORT", os.getenv("APP_PORT", "8899")))
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_DAYS: int = _env_int("JWT_EXPIRE_DAYS", 30)
    COOKIE_SECURE: bool = _env_bool("COOKIE_SECURE", IS_PRODUCTION)
    COOKIE_SAMESITE: str = os.getenv(
        "COOKIE_SAMESITE",
        "strict" if IS_PRODUCTION else "lax",
    )
    LOGIN_RATE_LIMIT_MAX_ATTEMPTS: int = _env_int("LOGIN_RATE_LIMIT_MAX_ATTEMPTS", 5)
    LOGIN_RATE_LIMIT_WINDOW_SECONDS: int = _env_int("LOGIN_RATE_LIMIT_WINDOW_SECONDS", 60)
    ENABLE_RATE_LIMIT: bool = _env_bool("ENABLE_RATE_LIMIT", True)


settings = Settings()
