from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.dependencies import get_current_user, get_upload_service
from app.schemas.common import APIResponse
from app.schemas.upload import ImportResponse
from app.services.upload_service import UploadService
from app.utils.request_context import get_request_id
from app.utils.responses import build_api_response

router = APIRouter(prefix="/upload", tags=["upload"], dependencies=[Depends(get_current_user)])


@router.post("/transactions", response_model=ImportResponse, status_code=status.HTTP_201_CREATED)
async def upload_transactions_csv(
    file: UploadFile = File(...),
    service: UploadService = Depends(get_upload_service),
) -> dict[str, object]:
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV files are supported.")
    try:
        summary = await service.import_csv(file)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {
        "status": "success",
        "message": "CSV import completed successfully.",
        "data": summary.model_dump(),
        "request_id": get_request_id(),
    }
