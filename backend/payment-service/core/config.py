"""Payment service configuration."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared.config import BaseAppSettings


class PaymentSettings(BaseAppSettings):
    APP_NAME: str = "Hena Wadeena Payment Service"
    APP_PORT: int = 8007
    DEBUG: bool = True
    PAYMENT_DATABASE_URL: str = "mysql+aiomysql://root:root@mysql:3306/hena_payment"


settings = PaymentSettings()
