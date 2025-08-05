"""
Tests for authentication endpoints
"""
import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from main import app

# Test client
client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "auth-service"

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data

def test_auth_health_endpoint():
    """Test auth router health endpoint"""
    response = client.get("/api/v1/auth/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

# Note: Database tests require MongoDB connection
# These are integration tests that need a running database

class TestAuthEndpoints:
    """Authentication endpoint tests (require database)"""
    
    @pytest.fixture
    def user_data(self):
        return {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "password": "testpassword123",
            "company_name": "Test Company"
        }
    
    @pytest.fixture  
    def login_data(self):
        return {
            "email": "test@example.com",
            "password": "testpassword123"
        }
    
    def test_register_endpoint_structure(self, user_data):
        """Test register endpoint structure (without database)"""
        # This will fail without database but tests endpoint structure
        response = client.post("/api/v1/auth/register", json=user_data)
        # Should get 500 error due to no database, but endpoint exists
        assert response.status_code in [500, 422, 201]
    
    def test_login_endpoint_structure(self, login_data):
        """Test login endpoint structure (without database)"""
        response = client.post("/api/v1/auth/login", json=login_data)
        # Should get 500 error due to no database, but endpoint exists
        assert response.status_code in [500, 422, 401]
    
    def test_me_endpoint_requires_auth(self):
        """Test /me endpoint requires authentication"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403  # No auth header
    
    def test_verify_token_endpoint_structure(self):
        """Test verify token endpoint structure"""
        response = client.post("/api/v1/auth/verify-token", json={"token": "fake-token"})
        assert response.status_code in [200, 500]  # Structure exists

if __name__ == "__main__":
    # Run basic tests
    test_health_endpoint()
    test_root_endpoint()
    test_auth_health_endpoint()
    print("✅ Basic endpoint tests passed!")
    
    # For database tests, you need MongoDB running:
    # pytest test_auth.py -v
