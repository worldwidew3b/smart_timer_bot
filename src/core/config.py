from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database settings
    database_url: str
    
    # Telegram bot settings
    telegram_bot_token: Optional[str] = None
    
    # API settings
    api_base_url: str = "http://localhost:8000"
    
    # Application settings
    app_title: str = "Smart Timer Bot API"
    app_version: str = "0.1.0"
    debug: bool = False
    
    class Config:
        env_file = ".env"


settings = Settings()