"""
Pydantic schemas for auth endpoints.

These define exactly what the API accepts and returns.
Pydantic validates every field — if a client sends bad data,
they get a clear 422 error instead of a database crash.
"""

from datetime import date, datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field


class SignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=4, max_length=72)
    dob: Optional[date] = None
    risk: Optional[str] = "moderate"


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class ProfileUpdateRequest(BaseModel):
    dob: Optional[date] = None
    risk: Optional[str] = None
    email: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=4, max_length=72)


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: Optional[str] = None
    date_of_birth: Optional[date] = None
    risk_tolerance: str
    created_at: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserResponse
