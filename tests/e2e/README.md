# End-to-End Tests

This directory contains end-to-end tests that test the complete user workflows.

## Running Tests

```bash
pytest tests/e2e/ -v
```

## Test Structure

- `test_user_workflows.py` - Tests complete user journeys
- `test_pricing_workflows.py` - Tests pricing rule creation and application
- `test_competitor_tracking.py` - Tests competitor tracking workflows
