from datetime import date
from math import ceil
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.dependencies import get_current_user, get_customer_service
from app.schemas.common import APIResponse
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate
from app.services.customer_service import CustomerService
from app.utils.request_context import get_request_id
from app.utils.responses import build_api_response

router = APIRouter(prefix="/customers", tags=["customers"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=APIResponse)
def list_customers(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    location: Optional[str] = Query(default=None),
    gender: Optional[str] = Query(default=None),
    service: CustomerService = Depends(get_customer_service),
) -> dict[str, object]:
    offset = (page - 1) * page_size
    filters = {"location": location, "gender": gender}
    customers, total = service.list_customers(offset=offset, limit=page_size, sort_by=sort_by, sort_order=sort_order, filters=filters)
    data = {
        "items": [CustomerRead.model_validate(customer).model_dump() for customer in customers],
        "meta": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": ceil(total / page_size) if total else 0,
        },
    }
    return build_api_response(status="success", message="Customers retrieved successfully.", data=data, request_id=get_request_id())


@router.get("/{customer_id}", response_model=APIResponse)
def get_customer(customer_id: str, service: CustomerService = Depends(get_customer_service)) -> dict[str, object]:
    customer = service.get_customer(customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")
    return build_api_response(status="success", message="Customer retrieved successfully.", data=CustomerRead.model_validate(customer).model_dump(), request_id=get_request_id())


@router.post("", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def create_customer(payload: CustomerCreate, service: CustomerService = Depends(get_customer_service)) -> dict[str, object]:
    try:
        customer = service.create_customer(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return build_api_response(status="success", message="Customer created successfully.", data=CustomerRead.model_validate(customer).model_dump(), request_id=get_request_id())


@router.put("/{customer_id}", response_model=APIResponse)
def update_customer(customer_id: str, payload: CustomerUpdate, service: CustomerService = Depends(get_customer_service)) -> dict[str, object]:
    try:
        customer = service.update_customer(customer_id, payload)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return build_api_response(status="success", message="Customer updated successfully.", data=CustomerRead.model_validate(customer).model_dump(), request_id=get_request_id())


@router.delete("/{customer_id}", response_model=APIResponse)
def delete_customer(customer_id: str, service: CustomerService = Depends(get_customer_service)) -> dict[str, object]:
    try:
        service.delete_customer(customer_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return build_api_response(status="success", message="Customer deleted successfully.", data={"customer_id": customer_id}, request_id=get_request_id())
