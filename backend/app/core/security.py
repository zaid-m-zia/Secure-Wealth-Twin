from __future__ import annotations

import base64
import hashlib
import hmac
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config.settings import Settings, get_settings
from app.schemas.auth import TokenPayload

bearer_scheme = HTTPBearer(auto_error=False)


def _urlsafe_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def _urlsafe_decode(token: str) -> bytes:
    padding = "=" * (-len(token) % 4)
    return base64.urlsafe_b64decode(token + padding)


def _json_dumps(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_token(
    subject: str,
    settings: Optional[Settings] = None,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[dict[str, Any]] = None,
    token_type: str = "access",
) -> str:
    active_settings = settings or get_settings()
    now = datetime.now(timezone.utc)
    expires = now + (expires_delta or timedelta(minutes=active_settings.access_token_expire_minutes))
    header = {"alg": active_settings.jwt_algorithm, "typ": "JWT"}
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
        "token_type": token_type,
        "jti": str(uuid.uuid4()),
    }
    if additional_claims:
        payload.update(additional_claims)

    header_segment = _urlsafe_encode(_json_dumps(header))
    payload_segment = _urlsafe_encode(_json_dumps(payload))
    signing_input = f"{header_segment}.{payload_segment}".encode("utf-8")
    signature = hmac.new(
        active_settings.secret_key.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    return f"{header_segment}.{payload_segment}.{_urlsafe_encode(signature)}"


def create_access_token(
    subject: str,
    settings: Optional[Settings] = None,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[dict[str, Any]] = None,
) -> str:
    return create_token(
        subject,
        settings=settings,
        expires_delta=expires_delta,
        additional_claims=additional_claims,
        token_type="access",
    )


def create_refresh_token(
    subject: str,
    settings: Optional[Settings] = None,
    additional_claims: Optional[dict[str, Any]] = None,
) -> str:
    active_settings = settings or get_settings()
    return create_token(
        subject,
        settings=active_settings,
        expires_delta=timedelta(days=active_settings.refresh_token_expire_days),
        additional_claims=additional_claims,
        token_type="refresh",
    )


def decode_token(
    token: str,
    settings: Optional[Settings] = None,
    expected_token_type: Optional[str] = None,
) -> TokenPayload:
    active_settings = settings or get_settings()
    try:
        header_segment, payload_segment, signature_segment = token.split(".", 2)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization token format.",
        ) from exc

    signing_input = f"{header_segment}.{payload_segment}".encode("utf-8")
    expected_signature = hmac.new(
        active_settings.secret_key.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    if not hmac.compare_digest(expected_signature, _urlsafe_decode(signature_segment)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization token signature.",
        )
    try:
        payload_data = json.loads(_urlsafe_decode(payload_segment).decode("utf-8"))
        expires_at = datetime.fromtimestamp(int(payload_data["exp"]), tz=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization token has expired.",
            )

        if expected_token_type and payload_data.get("token_type") != expected_token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization token type is invalid.",
            )

        return TokenPayload(**payload_data)
    except (KeyError, TypeError, ValueError, json.JSONDecodeError, Exception) as exc:
        if isinstance(exc, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization token payload.",
        ) from exc


def decode_access_token(token: str, settings: Optional[Settings] = None) -> TokenPayload:
    return decode_token(token, settings=settings, expected_token_type="access")


def decode_refresh_token(token: str, settings: Optional[Settings] = None) -> TokenPayload:
    return decode_token(token, settings=settings, expected_token_type="refresh")


async def get_token_from_request(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token is required.",
        )
    return credentials.credentials


async def get_current_token_payload(
    token: str = Depends(get_token_from_request),
    settings: Settings = Depends(get_settings),
) -> TokenPayload:
    return decode_access_token(token, settings=settings)
