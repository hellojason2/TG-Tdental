import os
from pydantic import BaseModel

class Settings(BaseModel):
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "postgresql://postgres:PuQAsTSyIMQOGjOYzjpqnkWbDHeHJjYr@shortline.proxy.rlwy.net:16355/railway")
    GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()
