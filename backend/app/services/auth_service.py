from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config.settings import Settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.models.audit_log import AuditLog
from app.models.user import User, UserSession
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.user_repository import UserRepository
from app.repositories.user_session_repository import UserSessionRepository
from app.schemas.auth import (
    CurrentUserResponse,
    LoginRequest,
    LogoutResponse,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
    TokenPairResponse,
    TokenPayload,
    UserProfile,
)


class AuthService:
    def __init__(
        self,
        session: Session,
        settings: Settings,
        user_repository: UserRepository,
        audit_log_repository: AuditLogRepository,
        user_session_repository: UserSessionRepository,
    ) -> None:
        self.session = session
        self.settings = settings
        self.user_repository = user_repository
        self.audit_log_repository = audit_log_repository
        self.user_session_repository = user_session_repository

    def register(self, payload: RegisterRequest, request_id: str) -> TokenPairResponse:
        if self.user_repository.get_by_email(payload.email):
            raise ValueError("A user with this email already exists.")

        user = User(
            full_name=payload.full_name,
            email=payload.email,
            password_hash=hash_password(payload.password),
        )
        self.session.add(user)
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise ValueError("A user with this email already exists.") from exc
        self.session.refresh(user)
        self._log_action(user.id, "register")
        return self._issue_tokens(user, message="Registration successful.", request_id=request_id)

    def login(self, payload: LoginRequest, request_id: str) -> TokenPairResponse:
        user = self.user_repository.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise ValueError("Invalid email or password.")
        self._log_action(user.id, "login")
        return self._issue_tokens(user, message="Login successful.", request_id=request_id)

    def refresh(self, payload: RefreshRequest, request_id: str) -> RefreshResponse:
        token_payload = decode_refresh_token(payload.refresh_token, settings=self.settings)
        if not token_payload.jti:
            raise ValueError("Refresh token session is invalid.")
        token_session = self.user_session_repository.get_by_token_id(token_payload.jti)
        if token_session is None or token_session.revoked:
            raise ValueError("Refresh token has been revoked.")
        token_session.revoked = True
        user = self.user_repository.get_by_email(token_payload.email or token_payload.sub)
        if user is None:
            raise ValueError("Unable to refresh tokens for this user.")
        return self._issue_tokens(user, message="Token refreshed successfully.", request_id=request_id)

    def logout(self, user: User, request_id: str) -> LogoutResponse:
        sessions, _ = self.user_session_repository.list(filters={"user_id": user.id}, limit=1000)
        for token_session in sessions:
            token_session.revoked = True
        self._log_action(user.id, "logout")
        return LogoutResponse(
            status="success",
            message="Logout successful.",
            request_id=request_id,
        )

    def current_user_response(self, user: User) -> CurrentUserResponse:
        return CurrentUserResponse.model_validate(user)

    def build_profile(self, user: User, access_token: str, refresh_token: str) -> TokenPairResponse:
        profile = UserProfile(
            subject=user.email,
            email=user.email,
            full_name=user.full_name,
            roles=["customer"],
            issued_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=self.settings.access_token_expire_minutes),
            claims={"user_id": user.id},
        )
        return TokenPairResponse(
            status="success",
            message="Authentication successful.",
            access_token=access_token,
            refresh_token=refresh_token,
            access_expires_in_seconds=self.settings.access_token_expire_minutes * 60,
            refresh_expires_in_seconds=self.settings.refresh_token_expire_days * 86400,
            profile=profile,
            request_id="-",
        )

    def _issue_tokens(self, user: User, *, message: str, request_id: str) -> TokenPairResponse:
        token_claims = {"email": user.email, "full_name": user.full_name, "roles": ["customer"]}
        refresh_token = create_refresh_token(
            subject=user.email,
            settings=self.settings,
            additional_claims=token_claims,
        )
        refresh_payload = decode_refresh_token(refresh_token, settings=self.settings)
        access_token = create_access_token(
            subject=user.email,
            settings=self.settings,
            expires_delta=timedelta(minutes=self.settings.access_token_expire_minutes),
            additional_claims=token_claims,
        )
        access_payload = decode_access_token(access_token, settings=self.settings)
        self.user_session_repository.extend(
            [
                UserSession(
                    user_id=user.id,
                    token_id=refresh_payload.jti or "",
                    expires_at=datetime.fromtimestamp(refresh_payload.exp, tz=timezone.utc),
                ),
                UserSession(
                    user_id=user.id,
                    token_id=access_payload.jti or "",
                    expires_at=datetime.fromtimestamp(access_payload.exp, tz=timezone.utc),
                ),
            ]
        )
        self.session.commit()
        profile = UserProfile(
            subject=user.email,
            email=user.email,
            full_name=user.full_name,
            roles=["customer"],
            issued_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=self.settings.access_token_expire_minutes),
            claims={"user_id": user.id},
        )
        return TokenPairResponse(
            status="success",
            message=message,
            access_token=access_token,
            refresh_token=refresh_token,
            access_expires_in_seconds=self.settings.access_token_expire_minutes * 60,
            refresh_expires_in_seconds=self.settings.refresh_token_expire_days * 86400,
            profile=profile,
            request_id=request_id,
        )

    def _log_action(self, user_id: int, action: str) -> None:
        self.audit_log_repository.add(AuditLog(user_id=user_id, action=action))
        self.session.commit()
