# Auth Service Documentation

## Overview
The Auth Service is a FastAPI-based microservice that handles authentication and authorization for the OmniPriceX platform using JWT tokens.

## Features
- ✅ User registration and login
- ✅ JWT access tokens with refresh tokens
- ✅ Password hashing with bcrypt
- ✅ Role-based access control
- ✅ Multi-tenant support (company-based)
- ✅ Token refresh and logout
- ✅ User profile management
- ✅ Health checks and monitoring

## API Endpoints

### Authentication Endpoints
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user  
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout user
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/verify-token` - Verify token validity

### Health & Monitoring
- `GET /health` - Service health check
- `GET /api/v1/auth/health` - Auth router health check
- `GET /` - Service information

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Copy `.env.example` to `.env` and update values:
```bash
cp .env.example .env
```

### 3. Start MongoDB
```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or use MongoDB Atlas (cloud)
# Update MONGODB_URL in .env with your connection string
```

### 4. Run the Service
```bash
# Development mode
python run.py

# Or with uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### 5. Access API Documentation
- Swagger UI: http://localhost:8001/api/v1/docs
- ReDoc: http://localhost:8001/api/v1/redoc

## Usage Examples

### Register a New User
```bash
curl -X POST "http://localhost:8001/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "newuser",
    "full_name": "New User",
    "password": "securepassword123",
    "company_name": "Tech Corp"
  }'
```

### Login User
```bash
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### Access Protected Endpoint
```bash
curl -X GET "http://localhost:8001/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Refresh Token
```bash
curl -X POST "http://localhost:8001/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

## Security Features

### Password Security
- Bcrypt hashing with configurable rounds (default: 12)
- Minimum password requirements enforced
- Salt generated automatically

### JWT Tokens
- HS256 algorithm (configurable)
- Short-lived access tokens (30 minutes)
- Long-lived refresh tokens (7 days)
- Token payload includes user ID, email, role, company

### Database Security
- Password hashes never stored in plain text
- Refresh tokens can be revoked
- User accounts can be deactivated

## Configuration

### Environment Variables
- `MONGODB_URL`: MongoDB connection string
- `SECRET_KEY`: JWT signing secret (use strong random key)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Access token lifetime
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token lifetime
- `BACKEND_CORS_ORIGINS`: Allowed frontend origins

### Security Settings
- `BCRYPT_ROUNDS`: Password hashing rounds (higher = more secure)
- `RATE_LIMIT_PER_MINUTE`: API rate limiting

## Database Schema

### User Document
```json
{
  "_id": "ObjectId",
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "hashed_password": "bcrypt_hash",
  "role": "user|admin|manager",
  "company_id": "optional_company_id",
  "company_name": "Company Name",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-01-01T00:00:00",
  "last_login": "2025-01-01T00:00:00"
}
```

### RefreshToken Document
```json
{
  "_id": "ObjectId", 
  "user_id": "user_object_id",
  "token": "hashed_refresh_token",
  "expires_at": "2025-01-01T00:00:00",
  "is_revoked": false,
  "user_agent": "browser_info",
  "ip_address": "client_ip",
  "created_at": "2025-01-01T00:00:00"
}
```

## Testing

### Run Tests
```bash
# Basic endpoint tests (no database required)
python test_auth.py

# Full test suite (requires MongoDB)
pytest test_auth.py -v
```

### Manual Testing
1. Start the service: `python run.py`
2. Open Swagger UI: http://localhost:8001/api/v1/docs
3. Test registration and login flows
4. Verify token refresh and logout

## Error Handling
- 400: Bad Request (invalid input)
- 401: Unauthorized (invalid credentials/token)
- 403: Forbidden (no auth header)
- 404: Not Found (user not found)
- 422: Validation Error (invalid data format)
- 500: Internal Server Error

## Monitoring & Logging
- Health endpoints for load balancer checks
- Structured logging with request tracking
- Error tracking and reporting
- Performance metrics collection

## Deployment Notes
- Use strong `SECRET_KEY` in production
- Enable HTTPS/TLS for token security
- Configure proper CORS origins
- Set up MongoDB replica sets for HA
- Use environment-specific configurations
- Monitor auth service logs and metrics

## Integration with Other Services
The auth service can be integrated with other microservices through:
- JWT token validation (shared secret)
- gRPC endpoints for service-to-service auth
- HTTP endpoints for frontend authentication
- Webhook notifications for user events
