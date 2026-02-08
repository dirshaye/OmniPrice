# E2E Tests (Playwright)

This directory contains browser-level smoke tests using Playwright.

## Why Playwright

For this project, Playwright is preferred over Selenium because:

- modern browser automation API
- reliable waits/locators
- faster setup for React apps

## Prerequisites

1. Backend and frontend must be running.
2. Playwright Chromium browser must be installed.

```bash
python -m playwright install chromium
```

## Run E2E

```bash
E2E_RUN=1 pytest -m e2e tests/e2e -v
```

Optional environment variables:

- `E2E_FRONTEND_URL` (default: `http://localhost:3000`)

## Coverage

Current smoke scope:

- Login page renders
- Register page navigation works
- Register form fields and submit button are visible
