"""API Gateway configuration."""

import sys
import os

# Add parent dir so shared module is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.config import BaseAppSettings


class GatewaySettings(BaseAppSettings):
    """Gateway-specific settings."""
    APP_NAME: str = "Hena Wadeena API Gateway"
    APP_PORT: int = 8000
    DEBUG: bool = True

    # Route → service URL mapping
    @property
    def service_routes(self) -> dict[str, str]:
        return {
            "/api/v1/auth": self.AUTH_SERVICE_URL,
            "/api/v1/users": self.USER_SERVICE_URL,
            "/api/v1/map": self.MAP_SERVICE_URL,
            "/api/v1/carpool": self.MAP_SERVICE_URL,
            "/api/v1/market": self.MARKET_SERVICE_URL,
            "/api/v1/listings": self.MARKET_SERVICE_URL,
            "/api/v1/guides": self.GUIDE_SERVICE_URL,
            "/api/v1/bookings": self.GUIDE_SERVICE_URL,
            "/api/v1/investments": self.INVESTMENT_SERVICE_URL,
            "/api/v1/payments": self.PAYMENT_SERVICE_URL,
            "/api/v1/wallet": self.PAYMENT_SERVICE_URL,
            "/api/v1/notifications": self.NOTIFICATION_SERVICE_URL,
            "/api/v1/search": self.SEARCH_SERVICE_URL,
            "/api/v1/ai": self.AI_SERVICE_URL,
        }


settings = GatewaySettings()
