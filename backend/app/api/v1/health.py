from time import perf_counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_app_settings, get_database_session
from app.schemas.common import APIResponse
from app.schemas.system import HealthData
from app.services.health_service import HealthService
from app.utils.request_context import get_request_id
from app.utils.responses import build_api_response

router = APIRouter(prefix="/health", tags=["health"])
_start_time = perf_counter()


@router.get("", response_model=APIResponse)
def get_health(session: Session = Depends(get_database_session)) -> dict[str, object]:
    settings = get_app_settings()
    service = HealthService(settings)
    payload = service.build_health_payload(session=session, uptime_seconds=perf_counter() - _start_time)
    return build_api_response(
        status="success",
        message="Service health retrieved successfully.",
        data=HealthData(**payload).model_dump(),
        request_id=get_request_id(),
    )
