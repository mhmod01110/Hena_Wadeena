"""JWT authentication middleware for the API Gateway."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response, JSONResponse

from shared.utils.jwt import decode_access_token

PUBLIC_PATHS = [
    "/health",
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/refresh",
    "/api/v1/auth/otp/request",
    "/api/v1/auth/otp/verify",
    "/docs",
    "/openapi.json",
    "/redoc",
]


def _is_public(path: str) -> bool:
    return any(path.startswith(p) for p in PUBLIC_PATHS)


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
