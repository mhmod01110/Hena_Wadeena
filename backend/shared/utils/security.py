"""Security utilities: password hashing, token hashing."""

import hashlib

from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt."""
    return _pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return _pwd_context.verify(plain, hashed)


def hash_token(token: str) -> str:
    """SHA-256 hash for refresh/OTP tokens before DB storage."""
    return hashlib.sha256(token.encode()).hexdigest()
