"""
Per-user dashboard settings: theme, accent color, live mode toggles.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserSettings(Base):
    __tablename__ = "settings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    theme_index: Mapped[int] = mapped_column(Integer, default=0)
    accent_color: Mapped[str] = mapped_column(String(7), default="#3cefb0")
    live_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    extended_hours: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="settings")
