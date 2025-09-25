from pydantic_settings import BaseSettings
from app.core.config import config

class Settings(BaseSettings):
    DATABASE_URL: str = config.DATABASE_URL
    REMINDER_INTERVAL_MINUTES: int = 120

settings = Settings()
