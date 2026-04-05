<<<<<<< HEAD
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/bloodbridge"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Email (Gmail SMTP — free)
    GMAIL_USER: Optional[str] = None         # your.email@gmail.com
    GMAIL_APP_PASSWORD: Optional[str] = None  # 16-char App Password from Google

    # Voice calls — Bland.ai (free trial) or leave empty for dev simulation
    BLAND_AI_API_KEY: Optional[str] = None

    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_MAPS_API_KEY: Optional[str] = None

    APP_BASE_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"

    HOSPITAL_NAME: str = "City Hospital"
    HOSPITAL_ADDRESS: str = "123 Medical Center Drive, City, State 12345"
    HOSPITAL_LAT: float = 40.7128
    HOSPITAL_LNG: float = -74.0060

    DEFAULT_SEARCH_RADIUS_KM: float = 25.0
    MAX_SEARCH_RADIUS_KM: float = 100.0
    CALL_TIMEOUT_SECONDS: int = 30
    NO_ANSWER_WAIT_SECONDS: int = 20

    class Config:
        env_file = ".env"
        extra = "ignore"
=======
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "blood_donor_system"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    frontend_origin: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
>>>>>>> a3f81144c587ef50313ffd6654e433970229adef


settings = Settings()
