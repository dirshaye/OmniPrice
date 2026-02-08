# Integration Tests

Integration tests validate API behavior across service boundaries.

## Run

```bash
pytest tests/integration -v
```

## Current Suites

- `test_vertical_slice.py`
  product -> competitor -> scraper -> price history flow
- `test_pricing_llm_slice.py`
  pricing recommendation + llm ask endpoints
- `test_error_paths.py`
  scraper/llm failure contracts

## Notes

- Tests use `httpx` with FastAPI ASGI transport.
- External providers are monkeypatched for deterministic behavior.
