"""Investment service configuration."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared.config import BaseAppSettings


class InvestmentSettings(BaseAppSettings):
    APP_NAME: str = "Hena Wadeena Investment Service"
    APP_PORT: int = 8006
    DEBUG: bool = True
    INVESTMENT_DATABASE_URL: str = "mysql+aiomysql://root:root@mysql:3306/hena_investment"


settings = InvestmentSettings()
