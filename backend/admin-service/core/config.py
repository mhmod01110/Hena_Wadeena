"""Admin service configuration."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared.config import BaseAppSettings


class AdminSettings(BaseAppSettings):
    APP_NAME: str = "Hena Wadeena Admin Service"
    APP_PORT: int = 8011
    DEBUG: bool = True
    ADMIN_DATABASE_URL: str = "mysql+aiomysql://root:root@mysql:3306/hena_admin"


settings = AdminSettings()
