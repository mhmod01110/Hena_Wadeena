"""JWT authentication middleware for the API Gateway."""

import os
import sys

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared.utils.jwt import decode_access_token

PUBLIC_PATHS = [
    "/health",
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/refresh",
    "/api/v1/auth/otp/request",
    "/api/v1/auth/otp/verify",
    "/api/v1/tourism",
    "/api/v1/market",
    "/api/v1/logistics",
    "/api/v1/investment",
    "/api/v1/guides",
    "/api/v1/search",
    "/api/v1/ai/chat",
    "/api/v1/map",
    "/docs",
    "/openapi.json",
    "/redoc",
]

PROTECTED_PATHS = [
    "/api/v1/users",
    "/api/v1/auth/me",
    "/api/v1/auth/logout",
    "/api/v1/payments",
    "/api/v1/notifications",
    "/api/v1/guides/bookings",
]


def _matches_prefix(path: str, prefixes: list[str]) -> bool:
    return any(path == prefix or path.startswith(prefix + "/") for prefix in prefixes)


def _is_public(path: str) -> bool:
    if _matches_prefix(path, PROTECTED_PATHS):
        return False
    return _matches_prefix(path, PUBLIC_PATHS)


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Validates JWT and injects X-User-Id / X-User-Role into request state."""

    def __init__(self, app, secret_key: str, algorithm: str = "HS256"):
        super().__init__(app)
        self.secret_key = secret_key
        self.algorithm = algorithm

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if _is_public(request.url.path):
            return await call_next(request)

        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return JSONResponse({"detail": "Missing Authorization header"}, status_code=401)

        payload = decode_access_token(auth.split(" ", 1)[1], self.secret_key, self.algorithm)
        if not payload:
            return JSONResponse({"detail": "Invalid or expired token"}, status_code=401)

        request.state.user_id = payload["sub"]
        request.state.user_role = payload["role"]
        request.state.token_jti = payload["jti"]

        return await call_next(request)
