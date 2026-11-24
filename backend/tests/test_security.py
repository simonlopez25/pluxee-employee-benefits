from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.core.config import settings
from app.core.errors import AppError
from app.core.security import (
    _decode_token,
    create_access_token,
    hash_password,
    verify_password,
)


def test_hash_and_verify_password():
    hashed = hash_password("Prueba123!")
    assert verify_password("Prueba123!", hashed) is True
    assert verify_password("otra", hashed) is False


def test_create_and_decode_access_token():
    token = create_access_token(1, "ADMIN")
    payload = _decode_token(token)
    assert payload["sub"] == "1"
    assert payload["role"] == "ADMIN"
    assert "iat" in payload
    assert "exp" in payload


def test_decode_expired_token():
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "1",
        "role": "ADMIN",
        "iat": int(now.timestamp()),
        "exp": int((now - timedelta(minutes=1)).timestamp()),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    with pytest.raises(AppError) as exc_info:
        _decode_token(token)
    assert exc_info.value.status_code == 401
    assert exc_info.value.code == "token_expired"


def test_decode_invalid_token():
    token = jwt.encode({"sub": "1"}, "wrong-secret-key-that-is-long-enough-32", algorithm="HS256")
    with pytest.raises(AppError) as exc_info:
        _decode_token(token)
    assert exc_info.value.status_code == 401
    assert exc_info.value.code == "invalid_token"