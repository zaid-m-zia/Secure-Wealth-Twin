from datetime import datetime, timezone

from pydantic import BaseModel, Field


class HealthData(BaseModel):
    status: str = Field(default="ok")
    database_status: str
    app_name: str
    environment: str
    uptime_seconds: float


class VersionData(BaseModel):
    app_name: str
    app_version: str
    environment: str
    api_version: str
    build_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
