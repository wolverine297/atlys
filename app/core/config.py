# app/core/config.py
from pydantic_settings import BaseSettings
from typing import ClassVar, Optional

class Settings(BaseSettings):
    API_TOKEN: str = "Jordan297"
    REDIS_URL: str = "redis://localhost:6379"
    BASE_URL: str = "https://dentalstall.com/shop/"
    DEFAULT_RETRY_ATTEMPTS: int = 3
    RETRY_DELAY: int = 5  # seconds
    LOCAL_STORAGE_PATH: str = "storage/products.json"
    IMAGE_STORAGE_PATH: str = "storage/images"
    SMTP_SERVER: ClassVar[str] = "smtp.gmail.com"
    SMTP_PORT: ClassVar[int] = 587
    EMAIL_SENDER: ClassVar[str] = "sourabhnangia29719@gmail.com"
    EMAIL_PASSWORD: ClassVar[str] = "Jordan297#$"
    EMAIL_RECIPIENT: ClassVar[str] = "nangiasourabh008@example.com"

    class Config:
        env_file = ".env"

settings = Settings()