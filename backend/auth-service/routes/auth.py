"""Auth service route handlers."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from database import get_db
from schemas import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    OTPRequestSchema,
    OTPVerifySchema,
    AuthResponse,
    TokenResponse,
)
from services.auth_service import (
    hash_password,
    verify_password,
    create_tokens,
    validate_refresh_token,
    revoke_refresh_token,
    log_auth_event,
)
from services.otp_service import create_otp, verify_otp
from config import settings

router = APIRouter()

# HTTP client for inter-service communication
http_client = httpx.AsyncClient(timeout=10.0)


# ── Register ─────────────────────────────────────────────────────────────────

@router.post("/register", response_model=AuthResponse)
async def register(
    data: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user. Creates user in user-service's DB, then issues tokens."""

    # Create user in user-service
    try:
        resp = await http_client.post(
            f"{settings.USER_SERVICE_URL}/internal/users",
            json={
                "email": data.email,
                "phone": data.phone,
                "full_name": data.full_name,
                "password_hash": hash_password(data.password),
                "role": data.role,
            },
        )

        if resp.status_code == 409:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email or phone already exists",
            )

        if resp.status_code != 201:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to create user in user-service",
            )

        user_data = resp.json()
        user_id = user_data["id"]

    except httpx.ConnectError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User service unavailable",
        )

    # Issue tokens
    tokens = await create_tokens(
        user_id=user_id,
        role=data.role,
        db=db,
        ip_address=request.client.host if request.client else None,
    )

    # Log event
    await log_auth_event(
        db=db,
        event_type="register",
        user_id=user_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return AuthResponse(
        success=True,
        message="تم إنشاء الحساب بنجاح",
        data=TokenResponse(**tokens),
    )


# ── Login ────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=AuthResponse)
async def login(
    data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Login with email/phone + password."""
    
    if not data.email and not data.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or phone is required",
        )

    # Fetch user from user-service
    try:
        lookup = data.email or data.phone
        lookup_type = "email" if data.email else "phone"
        resp = await http_client.get(
            f"{settings.USER_SERVICE_URL}/internal/users/lookup",
            params={lookup_type: lookup},
        )

        if resp.status_code == 404:
            await log_auth_event(db=db, event_type="failed_login",
                                 ip_address=request.client.host if request.client else None)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="بيانات الدخول غير صحيحة",
            )

        user_data = resp.json()

    except httpx.ConnectError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User service unavailable",
        )

    # Verify password
    if not verify_password(data.password, user_data["password_hash"]):
        await log_auth_event(
            db=db,
            event_type="failed_login",
            user_id=user_data["id"],
            ip_address=request.client.host if request.client else None,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="بيانات الدخول غير صحيحة",
        )

    # Check user status
    if user_data.get("status") != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="الحساب معلق أو محظور",
        )

    # Issue tokens
    tokens = await create_tokens(
        user_id=user_data["id"],
        role=user_data["role"],
        db=db,
        ip_address=request.client.host if request.client else None,
    )

    # Log event
    await log_auth_event(
        db=db,
        event_type="login",
        user_id=user_data["id"],
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return AuthResponse(
        success=True,
        message="تم تسجيل الدخول بنجاح",
        data=TokenResponse(**tokens),
    )


# ── Refresh Token ────────────────────────────────────────────────────────────

@router.post("/refresh", response_model=AuthResponse)
async def refresh(
    data: RefreshRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token using a valid refresh token."""

    record = await validate_refresh_token(data.refresh_token, db)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Revoke old refresh token (rotation)
    await revoke_refresh_token(data.refresh_token, db)

    # Fetch current user role from user-service
    try:
        resp = await http_client.get(
            f"{settings.USER_SERVICE_URL}/internal/users/{record.user_id}",
        )
        user_data = resp.json()
        role = user_data.get("role", "tourist")
    except Exception:
        role = "tourist"

    # Issue new tokens
    tokens = await create_tokens(
        user_id=str(record.user_id),
        role=role,
        db=db,
        ip_address=request.client.host if request.client else None,
    )

    return AuthResponse(
        success=True,
        message="Token refreshed",
        data=TokenResponse(**tokens),
    )


# ── Logout ───────────────────────────────────────────────────────────────────

@router.post("/logout")
async def logout(
    data: RefreshRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Logout: revoke refresh token."""

    await revoke_refresh_token(data.refresh_token, db)

    # Log event
    user_id = None
    if hasattr(request.state, "user_id"):
        user_id = request.state.user_id

    await log_auth_event(
        db=db,
        event_type="logout",
        user_id=user_id,
        ip_address=request.client.host if request.client else None,
    )

    return {"success": True, "message": "تم تسجيل الخروج بنجاح"}


# ── OTP Request ──────────────────────────────────────────────────────────────

@router.post("/otp/request")
async def request_otp(
    data: OTPRequestSchema,
    db: AsyncSession = Depends(get_db),
):
    """Request an OTP code (sent via SMS — mocked for now)."""
    otp = await create_otp(
        target=data.phone,
        purpose=data.purpose,
        db=db,
    )

    return {
        "success": True,
        "message": "تم إرسال رمز التحقق",
        # Only include in dev/debug mode for testing
        "debug_otp": otp if settings.DEBUG else None,
    }


# ── OTP Verify ───────────────────────────────────────────────────────────────

@router.post("/otp/verify", response_model=AuthResponse)
async def verify_otp_endpoint(
    data: OTPVerifySchema,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Verify an OTP code and issue tokens."""

    is_valid = await verify_otp(
        target=data.phone,
        code=data.code,
        purpose="login",
        db=db,
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="رمز التحقق غير صحيح أو منتهي الصلاحية",
        )

    # Look up or create user by phone
    try:
        resp = await http_client.get(
            f"{settings.USER_SERVICE_URL}/internal/users/lookup",
            params={"phone": data.phone},
        )

        if resp.status_code == 404:
            # Auto-register phone-only user
            resp = await http_client.post(
                f"{settings.USER_SERVICE_URL}/internal/users",
                json={
                    "phone": data.phone,
                    "full_name": data.phone,
                    "role": "tourist",
                },
            )
            if resp.status_code != 201:
                raise HTTPException(status_code=502, detail="Failed to create user")

        user_data = resp.json()

    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="User service unavailable")

    # Issue tokens
    tokens = await create_tokens(
        user_id=user_data["id"],
        role=user_data.get("role", "tourist"),
        db=db,
        ip_address=request.client.host if request.client else None,
    )

    return AuthResponse(
        success=True,
        message="تم تسجيل الدخول بنجاح",
        data=TokenResponse(**tokens),
    )
