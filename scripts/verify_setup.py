#!/usr/bin/env python3
"""Simple local verification script for OmniPrice backend."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from typing import Any

import requests

BASE_URL = os.getenv("VERIFY_BASE_URL", "http://localhost:8000")


def _wait_for_server(timeout_seconds: int = 20) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(1)
    return False


def _print_result(name: str, ok: bool, detail: str = "") -> None:
    status = "PASS" if ok else "FAIL"
    suffix = f" - {detail}" if detail else ""
    print(f"[{status}] {name}{suffix}")


def _json_request(method: str, path: str, payload: dict[str, Any] | None = None) -> requests.Response:
    return requests.request(method, f"{BASE_URL}{path}", json=payload, timeout=10)


def main() -> int:
    server_process: subprocess.Popen[str] | None = None

    try:
        # Start local server if not already up.
        try:
            health = requests.get(f"{BASE_URL}/health", timeout=2)
            already_running = health.status_code == 200
        except requests.RequestException:
            already_running = False

        if not already_running:
            print("Starting local backend server...")
            server_process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "omniprice.main:app", "--host", "127.0.0.1", "--port", "8000"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if not _wait_for_server():
                _print_result("backend startup", False, "server did not become healthy")
                return 1

        # Health
        health_resp = requests.get(f"{BASE_URL}/health", timeout=5)
        _print_result("GET /health", health_resp.status_code == 200, str(health_resp.status_code))

        # Register
        email = f"verify_{int(time.time())}@example.com"
        register_resp = _json_request(
            "POST",
            "/api/v1/auth/register",
            {
                "email": email,
                "password": "securepassword123",
                "full_name": "Verify User",
            },
        )
        _print_result("POST /api/v1/auth/register", register_resp.status_code == 201, str(register_resp.status_code))

        # Login JSON
        login_resp = _json_request(
            "POST",
            "/api/v1/auth/login/json",
            {
                "email": email,
                "password": "securepassword123",
            },
        )
        login_ok = login_resp.status_code == 200 and "access_token" in login_resp.json()
        _print_result("POST /api/v1/auth/login/json", login_ok, str(login_resp.status_code))

        # /me
        if login_ok:
            token = login_resp.json()["access_token"]
            me_resp = requests.get(
                f"{BASE_URL}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )
            _print_result("GET /api/v1/auth/me", me_resp.status_code == 200, str(me_resp.status_code))

        all_pass = (
            health_resp.status_code == 200
            and register_resp.status_code == 201
            and login_ok
        )
        return 0 if all_pass else 1

    finally:
        if server_process is not None:
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()


if __name__ == "__main__":
    raise SystemExit(main())
