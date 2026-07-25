from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_auth_service, get_current_user
from app.schemas.auth import (
    CurrentUserResponse,
    LoginRequest,
    LogoutResponse,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
    TokenPairResponse,
    ProfileUpdateRequest,
)
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.core.dependencies import get_user_service
from app.utils.request_context import get_request_id

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenPairResponse)
def register(payload: RegisterRequest, service: AuthService = Depends(get_auth_service)):
    try:
        return service.register(payload, request_id=get_request_id())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/login", response_model=TokenPairResponse)
def login(payload: LoginRequest, service: AuthService = Depends(get_auth_service)):
    try:
        return service.login(payload, request_id=get_request_id())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.post("/refresh", response_model=RefreshResponse)
def refresh(payload: RefreshRequest, service: AuthService = Depends(get_auth_service)):
    try:
        return service.refresh(payload, request_id=get_request_id())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.post("/logout", response_model=LogoutResponse)
def logout(service: AuthService = Depends(get_auth_service), current_user=Depends(get_current_user)):
    return service.logout(current_user, request_id=get_request_id())


@router.get("/profile", response_model=CurrentUserResponse)
def profile(current_user=Depends(get_current_user)):
    return CurrentUserResponse.model_validate(current_user)


@router.put("/profile", response_model=CurrentUserResponse)
def update_profile(
    payload: ProfileUpdateRequest,
    current_user=Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    return CurrentUserResponse.model_validate(service.update_user(current_user.id, payload))
