from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config.settings import get_settings
from app.core.cors import get_cors_origins
from app.core.database import initialize_database
from app.core.exception_handlers import install_exception_handlers
from app.middleware.request_id import RequestIdMiddleware
from app.utils.logger import configure_logging

settings = get_settings()
configure_logging(logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_origins(settings),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    install_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/", tags=["system"])
    def root() -> dict[str, object]:
        return {
            "status": "success",
            "message": f"{settings.app_name} foundation is running.",
            "data": {
                "app_version": settings.app_version,
                "environment": settings.environment,
            },
        }

    return app


app = create_app()
