import os
from pydantic import BaseModel


class Settings(BaseModel):
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/tdental")
    GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "change-me-in-production-" + os.urandom(8).hex())
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()
