from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class APIResponse(BaseModel):
    status: str = Field(..., examples=["success"])
    message: str
    data: Any = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    request_id: str


class ErrorResponse(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    request_id: str
    error_code: str
    description: str
    possible_solution: str


class MessageResponse(BaseModel):
    status: str = Field(default="success")
    message: str
    request_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
