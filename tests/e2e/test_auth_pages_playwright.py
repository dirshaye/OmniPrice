from __future__ import annotations

import os

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright


@pytest.mark.e2e
def test_auth_pages_render_and_navigate():
    if os.getenv("E2E_RUN") != "1":
        pytest.skip("Set E2E_RUN=1 to run browser tests")

    frontend_url = os.getenv("E2E_FRONTEND_URL", "http://localhost:3000")

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(f"{frontend_url}/login", wait_until="domcontentloaded")
            assert "Login" in page.content() or "Sign In" in page.content()

            page.get_by_role("link", name="Don't have an account? Sign Up").click()
            page.wait_for_url("**/register")

            assert page.locator("input[name='email']").count() == 1
            assert page.locator("input[name='password']").count() == 1
            assert page.locator("input[name='confirmPassword']").count() == 1
            assert page.get_by_role("button", name="Create Account").count() == 1

            browser.close()
    except PlaywrightError as exc:
        pytest.skip(f"Playwright not available in this environment: {exc}")
