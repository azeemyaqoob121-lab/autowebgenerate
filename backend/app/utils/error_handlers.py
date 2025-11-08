"""Custom exception handlers for standardized error responses"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from pydantic import ValidationError
from datetime import datetime
import logging
import uuid
from typing import Union

from app.utils.exceptions import APIException
from app.schemas.errors import (
    ErrorCode,
    ErrorDetail,
    ErrorResponse,
    ValidationErrorResponse
)

# Module logger
logger = logging.getLogger(__name__)


def get_request_id(request: Request) -> str:
    """
    Extract or generate request ID for error tracking.

    Args:
        request: FastAPI request object

    Returns:
        str: Request ID from request state or new UUID
    """
    # Try to get request_id from request state (set by middleware)
    if hasattr(request.state, 'request_id'):
        return request.state.request_id
    # Generate new UUID if not set
    return str(uuid.uuid4())


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """
    Handler for custom APIException instances.

    Transforms our custom exceptions into standardized ErrorResponse format.

    Args:
        request: FastAPI request object
        exc: APIException instance

    Returns:
        JSONResponse with ErrorResponse format
    """
    request_id = get_request_id(request)

    # Add request context to error details
    error_details = exc.details.copy()
    error_details['request_id'] = request_id
    error_details['timestamp'] = datetime.utcnow().isoformat() + 'Z'
    error_details['path'] = str(request.url.path)

    # Log the error with appropriate level
    if exc.status_code >= 500:
        logger.error(
            f"APIException: {exc.error_code} - {exc.message}",
            extra={
                'request_id': request_id,
                'status_code': exc.status_code,
                'error_code': exc.error_code,
                'path': request.url.path,
                'details': exc.details
            }
        )
    else:
        logger.warning(
            f"APIException: {exc.error_code} - {exc.message}",
            extra={
                'request_id': request_id,
                'status_code': exc.status_code,
                'error_code': exc.error_code,
                'path': request.url.path
            }
        )

    # Create error response
    error_response = ErrorResponse(
        error=ErrorDetail(
            code=exc.error_code,
            message=exc.message,
            details=error_details
        )
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handler for FastAPI's built-in HTTPException.

    Transforms HTTPException into our standardized ErrorResponse format.

    Args:
        request: FastAPI request object
        exc: HTTPException instance

    Returns:
        JSONResponse with ErrorResponse format
    """
    request_id = get_request_id(request)

    # Map HTTP status codes to error codes
    status_to_error_code = {
        status.HTTP_401_UNAUTHORIZED: ErrorCode.UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN: ErrorCode.FORBIDDEN,
        status.HTTP_404_NOT_FOUND: ErrorCode.NOT_FOUND,
        status.HTTP_422_UNPROCESSABLE_ENTITY: ErrorCode.VALIDATION_ERROR,
        status.HTTP_429_TOO_MANY_REQUESTS: ErrorCode.RATE_LIMIT_EXCEEDED,
        status.HTTP_500_INTERNAL_SERVER_ERROR: ErrorCode.INTERNAL_ERROR,
        status.HTTP_503_SERVICE_UNAVAILABLE: ErrorCode.SERVICE_UNAVAILABLE,
    }

    error_code = status_to_error_code.get(
        exc.status_code,
        ErrorCode.INTERNAL_ERROR
    )

    error_details = {
        'request_id': request_id,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'path': str(request.url.path)
    }

    # Log the error
    if exc.status_code >= 500:
        logger.error(
            f"HTTPException: {exc.status_code} - {exc.detail}",
            extra={
                'request_id': request_id,
                'status_code': exc.status_code,
                'path': request.url.path
            }
        )
    else:
        logger.warning(
            f"HTTPException: {exc.status_code} - {exc.detail}",
            extra={
                'request_id': request_id,
                'status_code': exc.status_code,
                'path': request.url.path
            }
        )

    # Create error response
    error_response = ErrorResponse(
        error=ErrorDetail(
            code=error_code,
            message=str(exc.detail),
            details=error_details
        )
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


async def validation_exception_handler(
    request: Request,
    exc: Union[RequestValidationError, ValidationError]
) -> JSONResponse:
    """
    Handler for Pydantic validation errors.

    Transforms RequestValidationError into our standardized ValidationErrorResponse format.

    Args:
        request: FastAPI request object
        exc: RequestValidationError or ValidationError instance

    Returns:
        JSONResponse with ValidationErrorResponse format
    """
    request_id = get_request_id(request)

    # Convert Pydantic errors to our format
    validation_response = ValidationErrorResponse.from_validation_errors(
        errors=exc.errors(),
        request_id=request_id
    )

    # Add path to error details
    if validation_response.error.details:
        validation_response.error.details['path'] = str(request.url.path)

    # Log validation error
    logger.warning(
        f"Validation error on {request.url.path}",
        extra={
            'request_id': request_id,
            'path': request.url.path,
            'errors': exc.errors()
        }
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=validation_response.model_dump()
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for any unhandled exceptions.

    Catches unexpected errors and returns a generic error response
    without exposing internal implementation details.

    Args:
        request: FastAPI request object
        exc: Exception instance

    Returns:
        JSONResponse with ErrorResponse format
    """
    request_id = get_request_id(request)

    # Log the full exception with traceback
    logger.exception(
        f"Unhandled exception: {type(exc).__name__} - {str(exc)}",
        extra={
            'request_id': request_id,
            'path': request.url.path,
            'exception_type': type(exc).__name__
        },
        exc_info=exc
    )

    # Create generic error response (don't expose internal details)
    error_details = {
        'request_id': request_id,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'path': str(request.url.path)
    }

    # In debug mode, include exception details
    # IMPORTANT: Never enable this in production!
    from app.config import settings
    if settings.DEBUG:
        error_details['exception_type'] = type(exc).__name__
        error_details['exception_message'] = str(exc)

    error_response = ErrorResponse(
        error=ErrorDetail(
            code=ErrorCode.INTERNAL_ERROR,
            message="An unexpected error occurred. Please try again later.",
            details=error_details
        )
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump()
    )


def register_exception_handlers(app) -> None:
    """
    Register all custom exception handlers with the FastAPI application.

    This function should be called during application initialization to
    ensure all exceptions are properly caught and formatted.

    Args:
        app: FastAPI application instance

    Usage:
        from app.utils.error_handlers import register_exception_handlers
        app = FastAPI()
        register_exception_handlers(app)
    """
    # Custom API exceptions
    app.add_exception_handler(APIException, api_exception_handler)

    # FastAPI HTTP exceptions
    app.add_exception_handler(HTTPException, http_exception_handler)

    # Pydantic validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)

    # Catch-all for unhandled exceptions
    app.add_exception_handler(Exception, unhandled_exception_handler)

    logger.info("Exception handlers registered successfully")
