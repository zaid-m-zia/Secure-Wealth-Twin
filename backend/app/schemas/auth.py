from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


EMAIL_PATTERN = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=254, pattern=EMAIL_PATTERN)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=254, pattern=EMAIL_PATTERN)
    password: str = Field(min_length=8, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=10)


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=120)


class TokenPayload(BaseModel):
    sub: str
    iat: int
    exp: int
    token_type: str = Field(default="access")
    jti: Optional[str] = None
    session_id: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    roles: list[str] = Field(default_factory=list)
    claims: dict[str, Any] = Field(default_factory=dict)


class UserProfile(BaseModel):
    subject: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    roles: list[str] = Field(default_factory=list)
    issued_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    claims: dict[str, Any] = Field(default_factory=dict)


class TokenPairResponse(BaseModel):
    status: str = Field(default="success")
    message: str
    access_token: str
    refresh_token: str
    token_type: str = Field(default="bearer")
    access_expires_in_seconds: int
    refresh_expires_in_seconds: int
    profile: UserProfile
    request_id: str


class LogoutResponse(BaseModel):
    status: str = Field(default="success")
    message: str
    request_id: str


class RefreshResponse(TokenPairResponse):
    pass


class CurrentUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str
    created_at: datetime
    updated_at: datetime
