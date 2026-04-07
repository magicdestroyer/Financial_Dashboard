"""
Dependency injection helpers for auth and user extraction.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from app.services.auth_service import decode_token

security = HTTPBearer()


async def get_current_user(credentials=Depends(security)) -> int:
    """
    Extract and verify JWT from Authorization header.
    Returns the user_id on success, raises 401 on failure.
    """
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    try:
        user_id = int(payload.get("sub", ""))
        return user_id
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
        )
