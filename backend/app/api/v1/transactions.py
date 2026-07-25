from datetime import date
from math import ceil
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status

from app.core.dependencies import get_current_user, get_transaction_service, get_upload_service
from app.schemas.common import APIResponse
from app.schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate
from app.services.transaction_service import TransactionService
from app.services.upload_service import UploadService
from app.schemas.upload import ImportResponse
from app.utils.request_context import get_request_id
from app.utils.responses import build_api_response

router = APIRouter(prefix="/transactions", tags=["transactions"], dependencies=[Depends(get_current_user)])


@router.post("/upload", response_model=ImportResponse, status_code=status.HTTP_201_CREATED)
async def upload_transactions_csv(
    file: UploadFile = File(...), service: UploadService = Depends(get_upload_service)
) -> dict[str, object]:
    if not file.filename or not file.filename.lower().endswith(".csv"):
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


@router.get("", response_model=APIResponse)
def list_transactions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    customer_id: Optional[str] = Query(default=None),
    transaction_date_from: Optional[date] = Query(default=None),
    transaction_date_to: Optional[date] = Query(default=None),
    service: TransactionService = Depends(get_transaction_service),
) -> dict[str, object]:
    offset = (page - 1) * page_size
    transactions, total = service.list_transactions(
        offset=offset,
        limit=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        customer_id=customer_id,
        transaction_date_from=transaction_date_from,
        transaction_date_to=transaction_date_to,
    )
    data = {
        "items": [TransactionRead.model_validate(transaction).model_dump() for transaction in transactions],
        "meta": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": ceil(total / page_size) if total else 0,
        },
    }
    return build_api_response(status="success", message="Transactions retrieved successfully.", data=data, request_id=get_request_id())




@router.get("/{transaction_id}", response_model=APIResponse)
def get_transaction(transaction_id: str, service: TransactionService = Depends(get_transaction_service)) -> dict[str, object]:
    transaction = service.get_transaction(transaction_id)
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found.")
    return build_api_response(status="success", message="Transaction retrieved successfully.", data=TransactionRead.model_validate(transaction).model_dump(), request_id=get_request_id())


@router.post("", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(payload: TransactionCreate, service: TransactionService = Depends(get_transaction_service)) -> dict[str, object]:
    try:
        transaction = service.create_transaction(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return build_api_response(status="success", message="Transaction created successfully.", data=TransactionRead.model_validate(transaction).model_dump(), request_id=get_request_id())


@router.put("/{transaction_id}", response_model=APIResponse)
def update_transaction(transaction_id: str, payload: TransactionUpdate, service: TransactionService = Depends(get_transaction_service)) -> dict[str, object]:
    try:
        transaction = service.update_transaction(transaction_id, payload)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return build_api_response(status="success", message="Transaction updated successfully.", data=TransactionRead.model_validate(transaction).model_dump(), request_id=get_request_id())


@router.delete("/{transaction_id}", response_model=APIResponse)
def delete_transaction(transaction_id: str, service: TransactionService = Depends(get_transaction_service)) -> dict[str, object]:
    try:
        service.delete_transaction(transaction_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return build_api_response(status="success", message="Transaction deleted successfully.", data={"transaction_id": transaction_id}, request_id=get_request_id())


@router.get("/statistics", response_model=APIResponse)
def transaction_statistics(service: TransactionService = Depends(get_transaction_service)) -> dict[str, object]:
    data = service.get_statistics()
    return build_api_response(status="success", message="Transaction statistics retrieved successfully.", data=data, request_id=get_request_id())
