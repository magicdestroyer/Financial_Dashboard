"""
Auth router — signup, login, refresh, profile, password change.

Every financial operation requires authentication, so this is
the first thing we build.  Once this works, all other routes
can simply add `user: User = Depends(get_current_user)`.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.settings import UserSettings
from app.schemas.auth import (
    SignupRequest, LoginRequest, RefreshRequest,
    ProfileUpdateRequest, PasswordChangeRequest,
    UserResponse, AuthResponse,
)
from app.services.auth_service import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
)
from app.middleware.auth import get_current_user

router = APIRouter()


@router.post("/signup", response_model=AuthResponse, status_code=201)
async def signup(req: SignupRequest, db: AsyncSession = Depends(get_db)):
    """Create a new account and return tokens."""
    # Check if username is taken
    existing = await db.execute(
        select(User).where(User.username.ilike(req.username))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Username already taken")

    # Create user
    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        date_of_birth=req.dob,
        risk_tolerance=req.risk or "moderate",
    )
    db.add(user)
    await db.flush()  # get the user.id before creating settings

    # Create default settings
    user_settings = UserSettings(user_id=user.id)
    db.add(user_settings)

    return AuthResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate and return tokens."""
    result = await db.execute(
        select(User).where(User.username.ilike(req.username))
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return AuthResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh")
async def refresh_token(req: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Exchange a refresh token for a new access token."""
    payload = decode_token(req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    from uuid import UUID
    user_id = UUID(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return {"access_token": create_access_token(user.id)}


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return UserResponse.model_validate(user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    req: ProfileUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update profile fields (DOB, risk tolerance, email)."""
    if req.dob is not None:
        user.date_of_birth = req.dob
    if req.risk is not None:
        if req.risk not in ("conservative", "moderate", "aggressive", "speculative"):
            raise HTTPException(status_code=422, detail="Invalid risk tolerance")
        user.risk_tolerance = req.risk
    if req.email is not None:
        user.email = req.email

    return UserResponse.model_validate(user)


@router.put("/password")
async def change_password(
    req: PasswordChangeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change password (requires current password)."""
    if not verify_password(req.old_password, user.password_hash):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    user.password_hash = hash_password(req.new_password)
    return {"message": "Password updated"}