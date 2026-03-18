"""Mock auth endpoints."""

import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# ── Dummy user store ─────────────────────────────────────────────────────────
USERS = {
    "admin@hena.com": {
        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "email": "admin@hena.com",
        "phone": "01012345678",
        "full_name": "أحمد محمد",
        "display_name": "أحمد",
        "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200",
        "role": "admin",
        "status": "active",
        "language": "ar",
        "password": "123456",
    },
    "tourist@hena.com": {
        "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
        "email": "tourist@hena.com",
        "phone": "01098765432",
        "full_name": "سارة أحمد",
        "display_name": "سارة",
        "avatar_url": "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=200",
        "role": "tourist",
        "status": "active",
        "language": "ar",
        "password": "123456",
    },
}

CURRENT_USER = None


class LoginReq(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str


class RegisterReq(BaseModel):
    email: str
    phone: str
    full_name: str
    password: str
    role: str = "tourist"


@router.post("/login")
def login(body: LoginReq):
    global CURRENT_USER
    user = USERS.get(body.email)
    if not user or user["password"] != body.password:
        raise HTTPException(401, "بيانات الدخول غير صحيحة")
    CURRENT_USER = user
    return {
        "success": True,
        "message": "تم تسجيل الدخول بنجاح",
        "data": {
            "access_token": f"mock-jwt-{user['id']}",
            "refresh_token": str(uuid.uuid4()),
            "token_type": "bearer",
            "expires_in": 900,
            "user": {k: v for k, v in user.items() if k != "password"},
        },
    }


@router.post("/register")
def register(body: RegisterReq):
    global CURRENT_USER
    new_id = str(uuid.uuid4())
    user = {
        "id": new_id,
        "email": body.email,
        "phone": body.phone,
        "full_name": body.full_name,
        "display_name": body.full_name.split()[0],
        "avatar_url": None,
        "role": body.role,
        "status": "active",
        "language": "ar",
        "password": body.password,
    }
    USERS[body.email] = user
    CURRENT_USER = user
    return {
        "success": True,
        "message": "تم إنشاء الحساب بنجاح",
        "data": {
            "access_token": f"mock-jwt-{new_id}",
            "refresh_token": str(uuid.uuid4()),
            "token_type": "bearer",
            "expires_in": 900,
            "user": {k: v for k, v in user.items() if k != "password"},
        },
    }


@router.get("/me")
def get_me():
    if CURRENT_USER:
        return {k: v for k, v in CURRENT_USER.items() if k != "password"}
    # Return default user for demo
    u = USERS["tourist@hena.com"]
    return {k: v for k, v in u.items() if k != "password"}


@router.post("/logout")
def logout():
    global CURRENT_USER
    CURRENT_USER = None
    return {"success": True, "message": "تم تسجيل الخروج بنجاح"}
