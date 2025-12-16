"""
API Package - REST API Route Handlers

This package contains all API endpoints organized by version.
Routes are thin - they only handle HTTP concerns:
- Request validation (using Pydantic schemas)
- Calling service layer for business logic
- Returning HTTP responses

Business logic lives in modules/, not here!
"""
