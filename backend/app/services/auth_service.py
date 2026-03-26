"""
Authentication service — password hashing and JWT creation.

Why separate from the router?  Because business logic (hashing,
token creation) shouldn't live inside HTTP handlers.  This makes
it testable and reusable.
"""

from datetime import datetime, timedelta
from uuid import UUID

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings

# bcrypt context — handles hashing and verification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt.
    
    bcrypt has a 72-byte limit, so truncate longer passwords.
    """
    return pwd_context.hash(password[:72])


def verify_password(plain: str, hashed: str) -> bool:
    """Check a plaintext password against its bcrypt hash.
    
    Apply the same 72-byte truncation as hash_password for consistency.
    """
    return pwd_context.verify(plain[:72], hashed)


def create_access_token(user_id: UUID) -> str:
    """
    Create a short-lived JWT for API authentication.
    Contains: sub (user ID), exp (expiration), type.
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: UUID) -> str:
    """
    Create a long-lived JWT for obtaining new access tokens.
    The user doesn't need to re-enter their password for 30 days.
    """
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    """
    Decode and validate a JWT.  Returns the payload dict or None if invalid.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
