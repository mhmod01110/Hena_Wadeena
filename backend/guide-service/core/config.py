"""Guide service configuration."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared.config import BaseAppSettings


class GuideSettings(BaseAppSettings):
    APP_NAME: str = "Hena Wadeena Guide Service"
    APP_PORT: int = 8005
    DEBUG: bool = True
    GUIDE_DATABASE_URL: str = "mysql+aiomysql://root:root@mysql:3306/hena_guide"


settings = GuideSettings()
