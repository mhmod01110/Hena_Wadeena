"""Analytics service configuration."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared.config import BaseAppSettings


class AnalyticsSettings(BaseAppSettings):
    APP_NAME: str = "Hena Wadeena Analytics Service"
    APP_PORT: int = 8012
    DEBUG: bool = True
    ANALYTICS_DATABASE_URL: str = "mysql+aiomysql://root:root@mysql:3306/hena_analytics"


settings = AnalyticsSettings()
