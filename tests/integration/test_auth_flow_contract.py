from __future__ import annotations

import os
from datetime import datetime
from types import SimpleNamespace

import httpx
import pytest
from bson import ObjectId

os.environ["DEBUG"] = "false"

import omniprice.main as main_module
from omniprice.main import app
from omniprice.services.auth import AuthService


@pytest.mark.asyncio
async def test_auth_register_login_and_me_contract(monkeypatch):
    async def _noop_init_db():
        return None

    user = SimpleNamespace(
        id=ObjectId(),
        email="flow@test.com",
        full_name="Flow User",
        is_active=True,
        created_at=datetime.utcnow(),
    )

    async def _register_user(payload):
        assert payload.email == "flow@test.com"
        return user

    async def _authenticate_user(email: str, password: str):
        assert email == "flow@test.com"
        assert password == "password123"
        return user

    async def _get_user_by_email(email: str):
        assert email == "flow@test.com"
        return user

    monkeypatch.setattr(main_module, "init_db", _noop_init_db)
    monkeypatch.setattr(AuthService, "register_user", staticmethod(_register_user))
    monkeypatch.setattr(AuthService, "authenticate_user", staticmethod(_authenticate_user))
    monkeypatch.setattr(AuthService, "get_user_by_email", staticmethod(_get_user_by_email))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "flow@test.com",
                "password": "password123",
                "full_name": "Flow User",
            },
        )
        assert register_response.status_code == 201
        registered = register_response.json()
        assert registered["id"] == str(user.id)
        assert registered["email"] == "flow@test.com"

        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={"email": "flow@test.com", "password": "password123"},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        assert isinstance(token, str) and token

        me_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_response.status_code == 200
        me = me_response.json()
        assert me["id"] == str(user.id)
        assert me["email"] == "flow@test.com"
