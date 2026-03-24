from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class SettingsResponse(BaseModel):
    theme_index: int
    accent_color: str
    live_enabled: bool
    extended_hours: bool

    class Config:
        from_attributes = True


class SettingsUpdateRequest(BaseModel):
    theme_index: Optional[int] = None
    accent_color: Optional[str] = None
    live_enabled: Optional[bool] = None
    extended_hours: Optional[bool] = None