from app.config.settings import get_settings
from app.core.security import create_access_token, decode_access_token, hash_password, verify_password


def test_password_hash_round_trip() -> None:
    hashed = hash_password("StrongPass123!")
    assert verify_password("StrongPass123!", hashed)
    assert not verify_password("wrong-password", hashed)


def test_jwt_round_trip() -> None:
    settings = get_settings()
    token = create_access_token(
        subject="demo-user",
        settings=settings,
        additional_claims={"email": "demo@example.com", "full_name": "Demo User", "roles": ["customer"]},
    )
    payload = decode_access_token(token, settings=settings)
    assert payload.sub == "demo-user"
    assert payload.email == "demo@example.com"
    assert payload.full_name == "Demo User"
    assert payload.roles == ["customer"]
