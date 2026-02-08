from __future__ import annotations

import pytest
from fastapi import HTTPException

from omniprice.core.security import create_access_token, decode_token, hash_password, verify_password


def test_hash_and_verify_password():
    hashed = hash_password("super-secret-password")
    assert hashed != "super-secret-password"
    assert verify_password("super-secret-password", hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_access_token_roundtrip_contains_subject_and_type():
    token = create_access_token({"sub": "unit@test.local"})
    payload = decode_token(token)
    assert payload["sub"] == "unit@test.local"
    assert payload["type"] == "access"


def test_decode_invalid_token_raises_http_401():
    with pytest.raises(HTTPException) as exc_info:
        decode_token("not-a-jwt")
    assert exc_info.value.status_code == 401
