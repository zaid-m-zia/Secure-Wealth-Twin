from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.dependencies import get_current_user, get_user_service
from app.schemas.common import APIResponse
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.user_service import UserService
from app.utils.request_context import get_request_id
from app.utils.responses import build_api_response

router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=APIResponse)
def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    service: UserService = Depends(get_user_service),
) -> dict[str, object]:
    offset = (page - 1) * page_size
    users, total = service.list_users(offset=offset, limit=page_size, sort_by=sort_by, sort_order=sort_order)
    data = {
        "items": [UserRead.model_validate(user).model_dump() for user in users],
        "meta": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": ceil(total / page_size) if total else 0,
        },
    }
    return build_api_response(status="success", message="Users retrieved successfully.", data=data, request_id=get_request_id())


@router.get("/{user_id}", response_model=APIResponse)
def get_user(user_id: int, service: UserService = Depends(get_user_service)) -> dict[str, object]:
    user = service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return build_api_response(status="success", message="User retrieved successfully.", data=UserRead.model_validate(user).model_dump(), request_id=get_request_id())


@router.post("", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, service: UserService = Depends(get_user_service)) -> dict[str, object]:
    try:
        user = service.create_user(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return build_api_response(status="success", message="User created successfully.", data=UserRead.model_validate(user).model_dump(), request_id=get_request_id())


@router.put("/{user_id}", response_model=APIResponse)
def update_user(user_id: int, payload: UserUpdate, service: UserService = Depends(get_user_service)) -> dict[str, object]:
    try:
        user = service.update_user(user_id, payload)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return build_api_response(status="success", message="User updated successfully.", data=UserRead.model_validate(user).model_dump(), request_id=get_request_id())


@router.delete("/{user_id}", response_model=APIResponse)
def delete_user(user_id: int, service: UserService = Depends(get_user_service)) -> dict[str, object]:
    try:
        service.delete_user(user_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return build_api_response(status="success", message="User deleted successfully.", data={"user_id": user_id}, request_id=get_request_id())
