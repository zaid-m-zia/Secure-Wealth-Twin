from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config.settings import Settings


class HealthService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def check_database(self, session: Session) -> str:
        try:
            session.execute(text("SELECT 1"))
            return "available"
        except SQLAlchemyError:
            return "unavailable"

    def build_health_payload(self, session: Session, uptime_seconds: float) -> dict[str, object]:
        return {
            "status": "ok",
            "database_status": self.check_database(session),
            "app_name": self._settings.app_name,
            "environment": self._settings.environment,
            "uptime_seconds": round(uptime_seconds, 3),
        }
