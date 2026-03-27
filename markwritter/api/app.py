"""FastAPI application factory and configuration.

This module provides:
- Application factory pattern for creating FastAPI apps
- CORS middleware configuration
- Rate limiting middleware
- Exception handlers
- Health check endpoints
- Lifespan management
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Optional

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)

# Global app instance for singleton pattern
_app: Optional[FastAPI] = None


def get_client_identifier(request: Request) -> str:
    """Get client identifier for rate limiting.

    Uses X-Forwarded-For header if available (for reverse proxy setups),
    otherwise falls back to client IP.

    Args:
        request: FastAPI request object

    Returns:
        Client identifier string
    """
    # Check for X-Forwarded-For header (set by reverse proxies)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Take the first IP in the chain (original client)
        return forwarded.split(",")[0].strip()

    # Fall back to direct client address
    return get_remote_address(request)


# Create limiter instance
limiter = Limiter(
    key_func=get_client_identifier,
    default_limits=["100/minute"],  # Default rate limit
    storage_uri="memory://",  # Use in-memory storage (can be changed to Redis for production)
)


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    version: str
    vault_connected: bool = False


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: Optional[str] = None
    request_id: Optional[str] = None


class AppSettings(BaseModel):
    """Application settings."""

    title: str = "Markwritter API"
    description: str = "AI-native knowledge management tool - Obsidian + memU + AI Agent"
    version: str = "0.1.0"
    cors_origins: list[str] = ["http://localhost:3000"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    debug: bool = False


def create_app(
    settings: Optional[AppSettings] = None,
    vault_path: Optional[str] = None,
) -> FastAPI:
    """Create and configure a FastAPI application.

    Args:
        settings: Optional application settings
        vault_path: Optional path to Obsidian vault

    Returns:
        Configured FastAPI application
    """
    if settings is None:
        settings = AppSettings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        """Application lifespan manager."""
        # Startup
        logger.info(f"Starting {settings.title} v{settings.version}")
        if vault_path:
            logger.info(f"Vault path: {vault_path}")
        yield
        # Shutdown
        logger.info(f"Shutting down {settings.title}")

    app = FastAPI(
        title=settings.title,
        description=settings.description,
        version=settings.version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # Add rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    # Add rate limiting middleware (after CORS)
    app.add_middleware(SlowAPIMiddleware)

    # Register exception handlers
    _register_exception_handlers(app)

    # Register routes
    _register_routes(app, vault_path)

    return app


def get_app(
    settings: Optional[AppSettings] = None,
    vault_path: Optional[str] = None,
) -> FastAPI:
    """Get or create the global FastAPI application.

    Uses singleton pattern to ensure only one app instance exists.

    Args:
        settings: Optional application settings
        vault_path: Optional path to Obsidian vault

    Returns:
        FastAPI application instance
    """
    global _app
    if _app is None:
        _app = create_app(settings, vault_path)
    return _app


def _register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers for the application.

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle all unhandled exceptions."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "detail": str(exc) if app.debug else "An unexpected error occurred",
            },
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        """Handle ValueError exceptions."""
        logger.warning(f"ValueError: {exc}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Bad Request", "detail": str(exc)},
        )

    @app.exception_handler(FileNotFoundError)
    async def file_not_found_handler(request: Request, exc: FileNotFoundError) -> JSONResponse:
        """Handle FileNotFoundError exceptions."""
        logger.warning(f"FileNotFoundError: {exc}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Not Found", "detail": str(exc)},
        )


def _register_routes(app: FastAPI, vault_path: Optional[str] = None) -> None:
    """Register API routes.

    Args:
        app: FastAPI application instance
        vault_path: Optional path to Obsidian vault
    """

    @app.get(
        "/health",
        response_model=HealthResponse,
        tags=["Health"],
        summary="Health check endpoint",
        description="Returns the health status of the API",
    )
    async def health_check() -> HealthResponse:
        """Health check endpoint.

        Returns basic health information about the API.
        """
        vault_connected = vault_path is not None
        return HealthResponse(
            status="ok",
            version=app.version,
            vault_connected=vault_connected,
        )

    @app.get(
        "/health/ready",
        tags=["Health"],
        summary="Readiness check endpoint",
        description="Returns whether the API is ready to accept requests",
    )
    async def readiness_check() -> dict[str, Any]:
        """Readiness check endpoint.

        Returns whether the service is ready to accept requests.
        """
        # In production, check database connections, vault access, etc.
        return {
            "ready": True,
            "checks": {
                "api": True,
                "vault": vault_path is not None,
            },
        }

    @app.get(
        "/health/live",
        tags=["Health"],
        summary="Liveness check endpoint",
        description="Returns whether the API is alive",
    )
    async def liveness_check() -> dict[str, str]:
        """Liveness check endpoint.

        Returns whether the service is alive.
        Used by Kubernetes for liveness probes.
        """
        return {"status": "alive"}

    # Register additional routers
    from markwritter.api.routes import chat, content, explore, logs, notes, query, record, search, settings, skills

    # Configure explore routes with vault path
    if vault_path:
        explore.set_vault_path(vault_path)

    # Configure settings routes with data directory
    if vault_path:
        settings.init_settings(vault_path)

    app.include_router(settings.router, prefix="/api/v1/settings", tags=["Settings"])

    app.include_router(notes.router, prefix="/api/v1", tags=["Notes"])
    app.include_router(content.router, prefix="/api/v1/content", tags=["Content"])
    app.include_router(search.router, prefix="/api/v1", tags=["Search"])
    app.include_router(query.router, prefix="/api/v1/query", tags=["Query"])
    app.include_router(record.router, prefix="/api/v1/record", tags=["Record"])
    app.include_router(explore.router, prefix="/api/v1/explore", tags=["Explore"])

    # Register agent framework routes (from legacy api/)
    # Phase 2.2: Add /api/v1 prefix for consistency
    app.include_router(skills.router, prefix="/api/v1", tags=["Skills"])
    app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
    app.include_router(logs.router, prefix="/api/v1", tags=["Logs"])

    # Phase 2.2: Backward compatibility - keep old /api/* paths working
    # These routes are deprecated and will be removed in a future version
    app.include_router(skills.router, prefix="/api", tags=["Skills (Deprecated)"])
    app.include_router(chat.router, prefix="/api", tags=["Chat (Deprecated)"])
    app.include_router(logs.router, prefix="/api", tags=["Logs (Deprecated)"])
