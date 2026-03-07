"""
Auth controller — THIN HTTP layer.
Only handles: request parsing, status codes, response formatting.
All business logic delegated to AuthService / OTPService.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import APIRouter, Depends, HTTPException, status, Request
import httpx

from schemas.requests import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    OTPRequestSchema,
    OTPVerifySchema,
)
from schemas.responses import AuthResponse, TokenResponse
from services.auth_service import AuthService
from services.otp_service import OTPService
from core.dependencies import get_auth_service, get_otp_service
from core.config import settings

router = APIRouter()

# HTTP client for inter-service calls
_http = httpx.AsyncClient(timeout=10.0)


def _client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


# ── POST /register ───────────────────────────────────────────────────────────

@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    body: RegisterRequest,
    request: Request,
    auth_svc: AuthService = Depends(get_auth_service),
):
    # 1. Create user in user-service
    try:
        resp = await _http.post(
            f"{settings.USER_SERVICE_URL}/internal/users",
            json={
                "email": body.email,
                "phone": body.phone,
                "full_name": body.full_name,
                "password_hash": auth_svc.hash_password(body.password),
                "role": body.role,
            },
        )
    except httpx.ConnectError:
        raise HTTPException(503, "User service unavailable")

    if resp.status_code == 409:
        raise HTTPException(409, "User with this email or phone already exists")
    if resp.status_code != 201:
        raise HTTPException(502, "Failed to create user")

    user = resp.json()

    # 2. Issue tokens
    tokens = await auth_svc.issue_tokens(
        user_id=user["id"], role=body.role, ip_address=_client_ip(request),
    )

    # 3. Audit log
    await auth_svc.log_event("register", user["id"], _client_ip(request), request.headers.get("user-agent"))

    return AuthResponse(success=True, message="تم إنشاء الحساب بنجاح", data=TokenResponse(**tokens))


# ── POST /login ──────────────────────────────────────────────────────────────

@router.post("/login", response_model=AuthResponse)
async def login(
    body: LoginRequest,
    request: Request,
    auth_svc: AuthService = Depends(get_auth_service),
):
    if not body.email and not body.phone:
        raise HTTPException(400, "Email or phone is required")

    # 1. Lookup user
    try:
        lookup_type = "email" if body.email else "phone"
        resp = await _http.get(
            f"{settings.USER_SERVICE_URL}/internal/users/lookup",
            params={lookup_type: body.email or body.phone},
        )
    except httpx.ConnectError:
        raise HTTPException(503, "User service unavailable")

    if resp.status_code == 404:
        await auth_svc.log_event("failed_login", ip_address=_client_ip(request))
        raise HTTPException(401, "بيانات الدخول غير صحيحة")

    user = resp.json()

    # 2. Verify password
    if not auth_svc.verify_password(body.password, user["password_hash"]):
        await auth_svc.log_event("failed_login", user["id"], _client_ip(request))
        raise HTTPException(401, "بيانات الدخول غير صحيحة")

    if user.get("status") != "active":
        raise HTTPException(403, "الحساب معلق أو محظور")

    # 3. Issue tokens
    tokens = await auth_svc.issue_tokens(
        user_id=user["id"], role=user["role"], ip_address=_client_ip(request),
    )

    await auth_svc.log_event("login", user["id"], _client_ip(request), request.headers.get("user-agent"))

    return AuthResponse(success=True, message="تم تسجيل الدخول بنجاح", data=TokenResponse(**tokens))


# ── POST /refresh ────────────────────────────────────────────────────────────

@router.post("/refresh", response_model=AuthResponse)
async def refresh(
    body: RefreshRequest,
    request: Request,
    auth_svc: AuthService = Depends(get_auth_service),
):
    record = await auth_svc.validate_refresh_token(body.refresh_token)
    if not record:
        raise HTTPException(401, "Invalid or expired refresh token")

    # Get current role
    try:
        resp = await _http.get(f"{settings.USER_SERVICE_URL}/internal/users/{record.user_id}")
        role = resp.json().get("role", "tourist")
    except Exception:
        role = "tourist"

    tokens = await auth_svc.rotate_refresh_token(
        body.refresh_token, str(record.user_id), role, _client_ip(request),
    )

    return AuthResponse(success=True, message="Token refreshed", data=TokenResponse(**tokens))


# ── POST /logout ─────────────────────────────────────────────────────────────

@router.post("/logout")
async def logout(
    body: RefreshRequest,
    request: Request,
    auth_svc: AuthService = Depends(get_auth_service),
):
    await auth_svc.revoke_token(body.refresh_token)

    user_id = request.headers.get("X-User-Id")
    await auth_svc.log_event("logout", user_id, _client_ip(request))

    return {"success": True, "message": "تم تسجيل الخروج بنجاح"}


# ── POST /otp/request ────────────────────────────────────────────────────────

@router.post("/otp/request")
async def request_otp(
    body: OTPRequestSchema,
    otp_svc: OTPService = Depends(get_otp_service),
):
    code = await otp_svc.request_otp(body.phone, body.purpose)

    return {
        "success": True,
        "message": "تم إرسال رمز التحقق",
        "debug_otp": code if settings.DEBUG else None,
    }


# ── POST /otp/verify ────────────────────────────────────────────────────────

@router.post("/otp/verify", response_model=AuthResponse)
async def verify_otp(
    body: OTPVerifySchema,
    request: Request,
    otp_svc: OTPService = Depends(get_otp_service),
    auth_svc: AuthService = Depends(get_auth_service),
):
    if not await otp_svc.verify_otp(body.phone, body.code, "login"):
        raise HTTPException(400, "رمز التحقق غير صحيح أو منتهي الصلاحية")

    # Lookup or auto-create user
    try:
        resp = await _http.get(
            f"{settings.USER_SERVICE_URL}/internal/users/lookup",
            params={"phone": body.phone},
        )
        if resp.status_code == 404:
            resp = await _http.post(
                f"{settings.USER_SERVICE_URL}/internal/users",
                json={"phone": body.phone, "full_name": body.phone, "role": "tourist"},
            )
            if resp.status_code != 201:
                raise HTTPException(502, "Failed to create user")

        user = resp.json()
    except httpx.ConnectError:
        raise HTTPException(503, "User service unavailable")

    tokens = await auth_svc.issue_tokens(
        user_id=user["id"], role=user.get("role", "tourist"), ip_address=_client_ip(request),
    )

    return AuthResponse(success=True, message="تم تسجيل الدخول بنجاح", data=TokenResponse(**tokens))
