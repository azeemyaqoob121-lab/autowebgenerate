"""Request context middleware for tracking and logging requests"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging

from app.utils.logging_config import get_logger

# Module logger
logger = get_logger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware for request context tracking and logging.

    Features:
    - Generates unique request_id for each request
    - Tracks request duration
    - Logs incoming requests and outgoing responses
    - Adds request_id to response headers
    - Attaches context to request state for access in routes/handlers

    The request_id is useful for:
    - Tracing requests across logs
    - Debugging issues by correlating all logs for a single request
    - Client-side request tracking
    """

    def __init__(self, app: ASGIApp):
        """
        Initialize the middleware.

        Args:
            app: ASGI application instance
        """
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process each request and response.

        Args:
            request: Incoming HTTP request
            call_next: Callable to process the request

        Returns:
            Response: HTTP response with added context
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Attach request_id to request state for access in routes
        request.state.request_id = request_id

        # Record request start time
        start_time = time.time()

        # Extract request metadata
        method = request.method
        path = request.url.path
        query_params = str(request.url.query) if request.url.query else None
        client_host = request.client.host if request.client else "unknown"

        # Log incoming request
        logger.info(
            f"Incoming request: {method} {path}",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "query_params": query_params,
                "client_ip": client_host,
                "user_agent": request.headers.get("user-agent", "unknown"),
            }
        )

        # Process the request
        try:
            response = await call_next(request)
        except Exception as exc:
            # Log exception and re-raise
            duration = time.time() - start_time
            logger.error(
                f"Request failed: {method} {path}",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "duration_ms": round(duration * 1000, 2),
                    "error": str(exc),
                },
                exc_info=exc
            )
            raise

        # Calculate request duration
        duration = time.time() - start_time
        duration_ms = round(duration * 1000, 2)

        # Add request context to response headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(duration_ms)

        # Log outgoing response
        log_level = logging.INFO
        if response.status_code >= 500:
            log_level = logging.ERROR
        elif response.status_code >= 400:
            log_level = logging.WARNING

        logger.log(
            log_level,
            f"Outgoing response: {method} {path} - {response.status_code}",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            }
        )

        # Log slow requests (>1 second) as warnings
        if duration > 1.0:
            logger.warning(
                f"Slow request detected: {method} {path}",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "duration_ms": duration_ms,
                    "status_code": response.status_code,
                }
            )

        return response


def get_request_id(request: Request) -> str:
    """
    Extract request_id from request state.

    Args:
        request: FastAPI request object

    Returns:
        str: Request ID if available, otherwise generates new UUID

    Usage:
        from app.middleware.request_context import get_request_id

        @router.get("/example")
        async def example(request: Request):
            request_id = get_request_id(request)
            logger.info("Processing request", extra={"request_id": request_id})
    """
    if hasattr(request.state, 'request_id'):
        return request.state.request_id
    return str(uuid.uuid4())
