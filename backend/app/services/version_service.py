from app.config.settings import Settings


class VersionService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def build_version_payload(self) -> dict[str, str]:
        return {
            "app_name": self._settings.app_name,
            "app_version": self._settings.app_version,
            "environment": self._settings.environment,
            "api_version": self._settings.api_v1_prefix.lstrip("/") or "api/v1",
        }
