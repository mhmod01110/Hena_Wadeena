"""Shared enums used across services."""

from enum import Enum


class UserRole(str, Enum):
    TOURIST = "tourist"
    STUDENT = "student"
    INVESTOR = "investor"
    LOCAL_CITIZEN = "local_citizen"
    GUIDE = "guide"
    MERCHANT = "merchant"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"


class KYCStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class OTPPurpose(str, Enum):
    LOGIN = "login"
    RESET = "reset"
    VERIFY = "verify"


class AuthEventType(str, Enum):
    REGISTER = "register"
    LOGIN = "login"
    LOGOUT = "logout"
    FAILED_LOGIN = "failed_login"
    TOKEN_REFRESH = "token_refresh"
    PASSWORD_RESET = "password_reset"
