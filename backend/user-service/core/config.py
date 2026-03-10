"""User service configuration."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared.config import BaseAppSettings


class UserSettings(BaseAppSettings):
    APP_NAME: str = "Hena Wadeena User Service"
    APP_PORT: int = 8002
    DEBUG: bool = True
    USER_DATABASE_URL: str = "mysql+aiomysql://root:root@mysql:3306/hena_users"


settings = UserSettings()
