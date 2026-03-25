"""Markwritter API application.

This module provides the FastAPI application with:
- CORS middleware configuration
- Exception handling
- Health check endpoint
- API versioning support
"""

from markwritter.api.app import create_app, get_app

__all__ = ["create_app", "get_app"]
