"""Security utilities: password hashing, token hashing."""

import hashlib

import bcrypt

def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def hash_token(token: str) -> str:
    """SHA-256 hash for refresh/OTP tokens before DB storage."""
    return hashlib.sha256(token.encode()).hexdigest()
