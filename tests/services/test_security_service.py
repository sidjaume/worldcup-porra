from uuid import uuid4
from types import SimpleNamespace

import pytest

from app.services.errors import UnauthorizedError
from app.services.security import SecurityService


def settings(secret_key: str = "test-secret") -> SimpleNamespace:
    return SimpleNamespace(
        secret_key=secret_key,
        access_token_expire_minutes=15,
    )


def test_access_token_round_trip() -> None:
    service = SecurityService(settings())
    user_id = uuid4()

    token = service.create_access_token(user_id=user_id, email="user@example.com")
    payload = service.decode_access_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["email"] == "user@example.com"


def test_invalid_access_token_raises_unauthorized() -> None:
    service = SecurityService(settings())

    with pytest.raises(UnauthorizedError):
        service.decode_access_token("not-a-token")


def test_token_hash_is_stable_and_secret_based() -> None:
    first = SecurityService(settings("first"))
    second = SecurityService(settings("second"))

    assert first.token_hash("token") == first.token_hash("token")
    assert first.token_hash("token") != second.token_hash("token")
