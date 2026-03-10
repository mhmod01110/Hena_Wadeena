"""Shared configuration module."""

from pydantic_settings import BaseSettings


class BaseAppSettings(BaseSettings):
    """Base settings inherited by all microservices."""

    # Database
    DATABASE_URL: str = "mysql+aiomysql://root:root@mysql:3306/hena_wadeena"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # JWT
    JWT_SECRET_KEY: str = "hena-wadeena-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Service Discovery
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    USER_SERVICE_URL: str = "http://localhost:8002"
    MAP_SERVICE_URL: str = "http://localhost:8003"
    MARKET_SERVICE_URL: str = "http://localhost:8004"
    GUIDE_SERVICE_URL: str = "http://localhost:8005"
    INVESTMENT_SERVICE_URL: str = "http://localhost:8006"
    PAYMENT_SERVICE_URL: str = "http://localhost:8007"
    NOTIFICATION_SERVICE_URL: str = "http://localhost:8008"
    SEARCH_SERVICE_URL: str = "http://localhost:8009"
    AI_SERVICE_URL: str = "http://localhost:8010"

    # CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://hena-wadeena.com",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"
