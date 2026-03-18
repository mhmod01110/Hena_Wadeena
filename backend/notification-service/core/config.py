"""Notification service configuration."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared.config import BaseAppSettings


class NotificationSettings(BaseAppSettings):
    APP_NAME: str = "Hena Wadeena Notification Service"
    APP_PORT: int = 8008
    DEBUG: bool = True
    NOTIFICATION_DATABASE_URL: str = "mysql+aiomysql://root:root@mysql:3306/hena_notification"


settings = NotificationSettings()
