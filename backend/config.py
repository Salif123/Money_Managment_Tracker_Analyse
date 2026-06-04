import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./bill_manager.db"
    UPLOAD_DIR: str = "../uploads"
    SECRET_KEY: str = "changeme"

    # Try to load settings from .env file inside backend directory
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure the upload directory exists
upload_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), settings.UPLOAD_DIR))
os.makedirs(upload_path, exist_ok=True)
