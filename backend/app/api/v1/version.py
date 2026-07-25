from fastapi import APIRouter

from app.core.dependencies import get_app_settings
from app.schemas.common import APIResponse
from app.schemas.system import VersionData
from app.utils.request_context import get_request_id
from app.utils.responses import build_api_response
from app.services.version_service import VersionService

router = APIRouter(prefix="/version", tags=["version"])


@router.get("", response_model=APIResponse)
def get_version() -> dict[str, object]:
    settings = get_app_settings()
    service = VersionService(settings)
    payload = service.build_version_payload()
    return build_api_response(
        status="success",
        message="Application version retrieved successfully.",
        data=VersionData(**payload).model_dump(),
        request_id=get_request_id(),
    )
