"""Auth service configuration."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared.config import BaseAppSettings


class AuthSettings(BaseAppSettings):
    APP_NAME: str = "Hena Wadeena Auth Service"
    APP_PORT: int = 8001
    DEBUG: bool = True
    AUTH_DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/hena_auth"
    OTP_LENGTH: int = 6
    OTP_EXPIRE_MINUTES: int = 5
    OTP_MAX_ATTEMPTS: int = 3


settings = AuthSettings()
