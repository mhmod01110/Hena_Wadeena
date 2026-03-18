"""Market service configuration."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared.config import BaseAppSettings


class MarketSettings(BaseAppSettings):
    APP_NAME: str = "Hena Wadeena Market Service"
    APP_PORT: int = 8004
    DEBUG: bool = True
    MARKET_DATABASE_URL: str = "mysql+aiomysql://root:root@mysql:3306/hena_market"


settings = MarketSettings()
