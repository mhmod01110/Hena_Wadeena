"""Map service configuration."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared.config import BaseAppSettings


class MapSettings(BaseAppSettings):
    APP_NAME: str = "Hena Wadeena Map Service"
    APP_PORT: int = 8003
    DEBUG: bool = True
    MAP_DATABASE_URL: str = "mysql+aiomysql://root:root@mysql:3306/hena_map"


settings = MapSettings()
