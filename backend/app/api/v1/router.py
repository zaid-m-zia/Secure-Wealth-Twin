from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.customers import router as customers_router
from app.api.v1.health import router as health_router
from app.api.v1.intelligence import router as intelligence_router
from app.api.v1.transactions import router as transactions_router
from app.api.v1.upload import router as upload_router
from app.api.v1.users import router as users_router
from app.api.v1.version import router as version_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(version_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(customers_router)
api_router.include_router(transactions_router)
api_router.include_router(upload_router)
api_router.include_router(intelligence_router)
