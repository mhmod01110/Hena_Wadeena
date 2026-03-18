"""Media service configuration."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared.config import BaseAppSettings


class MediaSettings(BaseAppSettings):
    APP_NAME: str = "Hena Wadeena Media Service"
    APP_PORT: int = 8013
    DEBUG: bool = True
    MEDIA_DATABASE_URL: str = "mysql+aiomysql://root:root@mysql:3306/hena_media"


settings = MediaSettings()
