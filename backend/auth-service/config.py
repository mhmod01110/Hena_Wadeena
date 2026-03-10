"""Auth service configuration."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.config import BaseAppSettings


class AuthSettings(BaseAppSettings):
    """Auth service specific settings."""
    APP_NAME: str = "Hena Wadeena Auth Service"
    APP_PORT: int = 8001
    DEBUG: bool = True

    # Auth-specific DB (can be separate from user DB)
    AUTH_DATABASE_URL: str = "mysql+aiomysql://root:root@localhost:3307/hena_auth"

    # OTP
    OTP_LENGTH: int = 6
    OTP_EXPIRE_MINUTES: int = 5
    OTP_MAX_ATTEMPTS: int = 3


settings = AuthSettings()
