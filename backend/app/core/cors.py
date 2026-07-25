from app.config.settings import Settings


def get_cors_origins(settings: Settings) -> list[str]:
    return settings.cors_origins
