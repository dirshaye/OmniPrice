# Integration Tests

This directory contains integration tests that test the interaction between multiple services.

## Running Tests

```bash
pytest tests/integration/ -v
```

## Test Structure

- `test_api_gateway.py` - Tests API Gateway integration with services
- `test_service_communication.py` - Tests gRPC communication between services
- `test_database_operations.py` - Tests database operations across services
