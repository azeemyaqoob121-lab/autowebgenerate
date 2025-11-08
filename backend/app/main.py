"""FastAPI Application Entry Point with Factory Pattern"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Optional, Dict, Any
import logging

from .config import settings, Settings
from .database import get_db, engine
from .routes import auth, businesses, templates, evaluations
from .utils.logging_config import configure_logging, get_logger
from .utils.error_handlers import register_exception_handlers
from .utils.rate_limit import register_rate_limiter
from .utils.security import get_current_user
from .models import User
from .middleware.request_context import RequestContextMiddleware

# Configure structured logging before any other imports
configure_logging()

# Module logger
logger = get_logger(__name__)


def create_app(config_override: Optional[Settings] = None) -> FastAPI:
    """
    Application factory for creating configured FastAPI instances.

    This factory pattern enables:
    - Multiple app instances for testing with different configurations
    - Environment-specific setup (dev, test, production)
    - Easier dependency injection and mocking in tests
    - Clean separation of app initialization from application logic

    Args:
        config_override: Optional Settings instance to override default config.
                        Useful for testing with custom configurations.

    Returns:
        Configured FastAPI application instance
    """
    # Use override config if provided, otherwise use global settings
    app_settings = config_override or settings

    # Define OpenAPI tags for endpoint grouping
    tags_metadata = [
        {
            "name": "authentication",
            "description": "User registration, login, and JWT token management. "
                          "Authentication is required for all business endpoints.",
        },
        {
            "name": "businesses",
            "description": "Business CRUD operations with advanced filtering, pagination, and search. "
                          "Manage business data including website URLs, contact information, and evaluation scores.",
        },
        {
            "name": "evaluations",
            "description": "Website evaluation operations using Lighthouse scoring. "
                          "Evaluate website quality, performance, SEO, and accessibility.",
        },
        {
            "name": "health",
            "description": "System health checks and API status monitoring",
        },
    ]

    # Create FastAPI app instance with comprehensive OpenAPI metadata
    app = FastAPI(
        title="AutoWeb Outreach AI API",
        description="""
## Overview

AutoWeb Outreach AI automates lead generation for web development agencies by discovering
UK businesses, evaluating their websites, and generating AI-powered website previews.

## Key Features

* **Business Discovery**: Automated scraping of UK business directories
* **Website Evaluation**: Lighthouse-based performance and quality scoring
* **AI Template Generation**: GPT-4 powered website preview generation
* **Lead Management**: Comprehensive CRUD operations with filtering and search
* **Secure Authentication**: JWT-based authentication with refresh tokens

## Authentication

Most endpoints require authentication via JWT Bearer tokens:

1. **Register**: Create a new user account at `POST /api/auth/register`
2. **Login**: Get access and refresh tokens at `POST /api/auth/login`
3. **Authorize**: Click the 'Authorize' button and enter your access token
4. **Access Protected Endpoints**: Use authenticated requests to manage businesses

Access tokens expire after 24 hours. Use the refresh token endpoint to get a new access token.

## Rate Limiting

API endpoints are rate-limited to ensure fair usage:
- Authentication endpoints: 5 requests/minute
- Business endpoints: 100 requests/minute
- Rate limit headers are included in all responses

## Error Handling

All errors follow a standardized format with error codes, messages, and request IDs
for debugging. See the ErrorResponse schema for details.
        """,
        version=app_settings.API_VERSION,
        contact={
            "name": "AutoWeb Outreach AI Support",
            "email": "support@autoweb-ai.com",
            "url": "https://autoweb-ai.com/support",
        },
        license_info={
            "name": "Proprietary",
            "identifier": "Proprietary",
        },
        openapi_tags=tags_metadata,
        docs_url="/docs" if app_settings.DEBUG else None,  # Disable docs in production
        redoc_url="/redoc" if app_settings.DEBUG else None,
        swagger_ui_parameters={
            "deepLinking": True,
            "displayRequestDuration": True,
            "filter": True,
            "showExtensions": True,
            "showCommonExtensions": True,
        },
    )

    # Add request context middleware first (executed second due to reverse order)
    app.add_middleware(RequestContextMiddleware)

    # Configure CORS middleware last (executed first due to reverse order)
    # This ensures CORS headers are added to all responses including errors
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.CORS_ORIGINS,
        allow_credentials=app_settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=app_settings.CORS_ALLOW_METHODS,
        allow_headers=app_settings.CORS_ALLOW_HEADERS,
    )

    # Store settings in app state for access in route handlers
    app.state.settings = app_settings

    # Register exception handlers for standardized error responses
    register_exception_handlers(app)

    # Register rate limiter
    register_rate_limiter(app)

    # Configure OpenAPI security scheme for JWT authentication
    # This enables the "Authorize" button in Swagger UI
    from fastapi.openapi.utils import get_openapi

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            tags=app.openapi_tags,
        )

        # Add JWT Bearer security scheme
        openapi_schema["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Enter your JWT access token obtained from the login endpoint",
            }
        }

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    # Include API routers
    app.include_router(
        auth.router,
        prefix="/api/auth",
        tags=["authentication"]
    )
    app.include_router(
        businesses.router,
        prefix="/api/businesses",
        tags=["businesses"]
    )
    app.include_router(
        templates.router,
        prefix="/api",
        tags=["templates"]
    )
    app.include_router(
        evaluations.router,
        prefix="/api",
        tags=["evaluations"]
    )

    # Stats endpoint (separate from businesses router to avoid routing conflicts)
    @app.get(
        "/api/stats",
        tags=["businesses"],
        summary="Get dashboard statistics",
        description="Get statistics for dashboard: total businesses, qualified leads, templates generated"
    )
    async def get_dashboard_stats(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        """
        Get dashboard statistics.

        Returns:
        - total_businesses: Total number of businesses in database
        - qualified_leads: Number of businesses with score < 70
        - templates_generated: Total number of AI templates generated
        """
        from app.models import Business, Template
        from sqlalchemy import func

        try:
            # Get total businesses count (exclude deleted)
            total_businesses = db.query(func.count(Business.id)).filter(
                Business.deleted_at.is_(None)
            ).scalar() or 0

            # Get qualified leads count (score < 70 and not deleted)
            qualified_leads = db.query(func.count(Business.id)).filter(
                Business.deleted_at.is_(None),
                Business.score < 70,
                Business.score.isnot(None)
            ).scalar() or 0

            # Get total templates generated
            templates_generated = db.query(func.count(Template.id)).scalar() or 0

            return {
                "total_businesses": total_businesses,
                "qualified_leads": qualified_leads,
                "templates_generated": templates_generated
            }
        except Exception as e:
            logger.error(f"Failed to fetch dashboard stats: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch dashboard stats: {str(e)}"
            )


    @app.on_event("startup")
    async def startup_event():
        """
        Application startup event handler.

        Executes when the application starts:
        - Logs application startup with environment info
        - Verifies database connectivity
        - Initializes any required resources
        """
        logger.info(f"Starting {app_settings.APP_NAME} v{app_settings.API_VERSION}")
        logger.info(f"Environment: {app_settings.ENVIRONMENT}")
        logger.info(f"Debug mode: {app_settings.DEBUG}")
        logger.info(f"CORS origins: {', '.join(app_settings.CORS_ORIGINS)}")

        # Verify database connectivity
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            logger.warning("Application started but database is unavailable")

    @app.on_event("shutdown")
    async def shutdown_event():
        """
        Application shutdown event handler.

        Executes when the application shuts down:
        - Closes database connections gracefully
        - Cleans up resources
        - Logs shutdown event
        """
        logger.info("Shutting down application...")
        engine.dispose()
        logger.info("Database connections closed")

    @app.get(
        "/",
        tags=["health"],
        summary="API Information",
        response_description="API metadata and navigation links"
    )
    async def root():
        """
        Get API information and navigation links.

        Returns basic API metadata including version, environment, and links
        to documentation and health check endpoints.

        **No authentication required**
        """
        return {
            "message": app_settings.APP_NAME,
            "version": app_settings.API_VERSION,
            "environment": app_settings.ENVIRONMENT,
            "docs": "/docs",
            "health": "/api/health"
        }

    @app.get(
        "/api/health",
        tags=["health"],
        summary="Health Check",
        response_description="System health status"
    )
    async def health_check(db: Session = Depends(get_db)):
        """
        Check system health and database connectivity.

        Verifies:
        - Application is running
        - Database connection is available
        - Returns current timestamp and version

        **No authentication required**

        Returns:
            - **status**: Overall health status ("healthy")
            - **version**: API version
            - **environment**: Current environment (development/production)
            - **timestamp**: Current UTC timestamp
            - **database**: Database connection status ("connected" or "unavailable")
        """
        # Check database connectivity
        db_status = "connected"
        try:
            db.execute(text("SELECT 1"))
        except Exception as e:
            db_status = "unavailable"
            logger.warning(f"Health check: Database unavailable - {str(e)}")

        return {
            "status": "healthy",
            "version": app_settings.API_VERSION,
            "environment": app_settings.ENVIRONMENT,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "database": db_status
        }

    return app


# Create the default application instance
# This is the app instance used by uvicorn when running the application
app = create_app()
