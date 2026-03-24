"""Settings CRUD — theme, accent color, live mode."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.settings import UserSettings
from app.schemas.settings import SettingsResponse, SettingsUpdateRequest
from app.middleware.auth import get_current_user

router = APIRouter()


@router.get("", response_model=SettingsResponse)
async def get_settings(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == user.id)
    )
    s = result.scalar_one_or_none()
    if not s:
        s = UserSettings(user_id=user.id)
        db.add(s)
        await db.flush()
    return SettingsResponse.model_validate(s)


@router.put("", response_model=SettingsResponse)
async def update_settings(
    req: SettingsUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == user.id)
    )
    s = result.scalar_one_or_none()
    if not s:
        s = UserSettings(user_id=user.id)
        db.add(s)

    if req.theme_index is not None:
        s.theme_index = req.theme_index
    if req.accent_color is not None:
        s.accent_color = req.accent_color
    if req.live_enabled is not None:
        s.live_enabled = req.live_enabled
    if req.extended_hours is not None:
        s.extended_hours = req.extended_hours

    return SettingsResponse.model_validate(s)