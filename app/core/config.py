from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Ignore unrelated env vars (e.g. AWS_S3_*), so shared .env edits don't crash the service.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_ENV: Literal["local", "dev", "prod"] = "local"
    APP_NAME: str = "fsc-user-microservice"
    APP_VERSION: str = "0.1.0"
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    REDIS_URL: str = ""

    # OTP (spec): if Firebase not configured, uses a static dev code.
    OTP_TTL_SECONDS: int = 300
    OTP_STATIC_CODE: str = "123456"

    # Profile uploads: S3 if bucket set, else local disk + PUBLIC_APP_URL
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "ap-south-1"
    S3_BUCKET_NAME: str = ""
    S3_PUBLIC_BASE_URL: str = ""

    LOCAL_UPLOAD_DIR: str = "uploads"
    PUBLIC_APP_URL: str = "http://localhost:8001"
    UPLOAD_MAX_MB: int = Field(default=5, description="Max profile image size (MB)")

    # Set the same value on calling services (Order, Vehicle) as X-Internal-Api-Key
    INTERNAL_API_KEY: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[arg-type]


settings = get_settings()
