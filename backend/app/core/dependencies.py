from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.settings import Settings, get_settings
from app.core.security import get_current_token_payload
from app.database.session import get_db_session
from app.models.user import User
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from app.repositories.user_session_repository import UserSessionRepository
from app.schemas.auth import TokenPayload
from app.services.auth_service import AuthService
from app.services.customer_service import CustomerService
from app.services.transaction_service import TransactionService
from app.services.upload_service import UploadService
from app.services.user_service import UserService


def get_app_settings() -> Settings:
    return get_settings()


def get_database_session() -> Generator[Session, None, None]:
    yield from get_db_session()


def get_user_repository(session: Session = Depends(get_database_session)) -> UserRepository:
    return UserRepository(session)


def get_user_session_repository(session: Session = Depends(get_database_session)) -> UserSessionRepository:
    return UserSessionRepository(session)


def get_customer_repository(session: Session = Depends(get_database_session)) -> CustomerRepository:
    return CustomerRepository(session)


def get_transaction_repository(session: Session = Depends(get_database_session)) -> TransactionRepository:
    return TransactionRepository(session)


def get_audit_log_repository(session: Session = Depends(get_database_session)) -> AuditLogRepository:
    return AuditLogRepository(session)


def get_user_service(
    session: Session = Depends(get_database_session),
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(session, user_repository)


def get_customer_service(
    session: Session = Depends(get_database_session),
    customer_repository: CustomerRepository = Depends(get_customer_repository),
) -> CustomerService:
    return CustomerService(session, customer_repository)


def get_transaction_service(
    session: Session = Depends(get_database_session),
    transaction_repository: TransactionRepository = Depends(get_transaction_repository),
    customer_repository: CustomerRepository = Depends(get_customer_repository),
) -> TransactionService:
    return TransactionService(session, transaction_repository, customer_repository)


def get_upload_service(
    session: Session = Depends(get_database_session),
    customer_repository: CustomerRepository = Depends(get_customer_repository),
    transaction_repository: TransactionRepository = Depends(get_transaction_repository),
) -> UploadService:
    return UploadService(session, customer_repository, transaction_repository)


def get_auth_service(
    session: Session = Depends(get_database_session),
    settings: Settings = Depends(get_settings),
    user_repository: UserRepository = Depends(get_user_repository),
    audit_log_repository: AuditLogRepository = Depends(get_audit_log_repository),
    user_session_repository: UserSessionRepository = Depends(get_user_session_repository),
) -> AuthService:
    return AuthService(session, settings, user_repository, audit_log_repository, user_session_repository)


def get_current_user(
    token_payload: TokenPayload = Depends(get_current_token_payload),
    user_repository: UserRepository = Depends(get_user_repository),
    user_session_repository: UserSessionRepository = Depends(get_user_session_repository),
) -> User:
    user = None
    if token_payload.email:
        user = user_repository.get_by_email(token_payload.email)
    if user is None and token_payload.sub:
        user = user_repository.get_by_email(token_payload.sub)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User could not be resolved.")
    if token_payload.jti:
        session = user_session_repository.get_by_token_id(token_payload.jti)
        if session is not None and session.revoked:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization token has been revoked.")
    return user


async def get_authenticated_token(payload: TokenPayload = Depends(get_current_token_payload)) -> TokenPayload:
    return payload
