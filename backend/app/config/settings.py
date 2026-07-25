from functools import lru_cache
from typing import Any

from pydantic import BaseModel, Field


class Settings(BaseModel):
    app_name: str = Field(default="SecureWealth AI")
    app_version: str = Field(default="0.1.0")
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    api_v1_prefix: str = Field(default="/api/v1")
    database_url: str = Field(
        default="postgresql+psycopg2://securewealth:securewealth@localhost:5432/securewealth"
    )
    secret_key: str = Field(default="change-me-in-production")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=60, ge=1)
    refresh_token_expire_days: int = Field(default=30, ge=1)
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    @classmethod
    def from_env(cls) -> "Settings":
        import os

        cors_value = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
        cors_origins = [origin.strip() for origin in cors_value.split(",") if origin.strip()]
        return cls(
            app_name=os.getenv("APP_NAME", "SecureWealth AI"),
            app_version=os.getenv("APP_VERSION", "0.1.0"),
            environment=os.getenv("ENVIRONMENT", "development"),
            debug=os.getenv("DEBUG", "true").lower() in {"1", "true", "yes", "on"},
            api_v1_prefix=os.getenv("API_V1_PREFIX", "/api/v1"),
            database_url=os.getenv(
                "DATABASE_URL",
                "postgresql+psycopg2://securewealth:securewealth@localhost:5432/securewealth",
            ),
            secret_key=os.getenv("SECRET_KEY", "change-me-in-production"),
            jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
            access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
            refresh_token_expire_days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30")),
            cors_origins=cors_origins,
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_env()


settings = get_settings()
