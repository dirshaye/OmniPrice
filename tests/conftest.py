"""
Test configuration and fixtures for OmniPriceX tests.
"""

import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db():
    """Provide a test database."""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.test_omnipricex
    yield db
    await client.drop_database("test_omnipricex")
    client.close()

@pytest.fixture
async def api_client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an HTTP client for API testing."""
    async with AsyncClient(base_url="http://localhost:8000") as client:
        yield client
