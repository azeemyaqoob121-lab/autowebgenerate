"""Custom exception classes for standardized error handling"""
from typing import Optional, Dict, Any
from fastapi import status

from app.schemas.errors import ErrorCode


class APIException(Exception):
    """
    Base exception class for all API errors.

    All custom exceptions should inherit from this class to ensure
    consistent error handling across the application.

    Attributes:
        status_code: HTTP status code for the error
        error_code: Machine-readable error code from ErrorCode constants
        message: Human-readable error message
        details: Optional additional context for debugging
    """

    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class BusinessNotFoundException(APIException):
    """
    Raised when a business resource cannot be found.

    Usage:
        raise BusinessNotFoundException(business_id="123e4567-...")
    """

    def __init__(
        self,
        business_id: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        default_message = "Business not found"
        if business_id:
            default_message = f"Business with ID {business_id} not found"

        final_details = details or {}
        if business_id:
            final_details["business_id"] = business_id

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.BUSINESS_NOT_FOUND,
            message=message or default_message,
            details=final_details
        )


class UserNotFoundException(APIException):
    """
    Raised when a user resource cannot be found.

    Usage:
        raise UserNotFoundException(user_id="123e4567-...")
    """

    def __init__(
        self,
        user_id: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        default_message = "User not found"
        if user_id:
            default_message = f"User with ID {user_id} not found"

        final_details = details or {}
        if user_id:
            final_details["user_id"] = user_id

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.USER_NOT_FOUND,
            message=message or default_message,
            details=final_details
        )


class ResourceNotFoundException(APIException):
    """
    Generic not found exception for any resource type.

    Usage:
        raise ResourceNotFoundException(
            resource_type="Template",
            resource_id="123e4567-..."
        )
    """

    def __init__(
        self,
        resource_type: str,
        resource_id: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        default_message = f"{resource_type} not found"
        if resource_id:
            default_message = f"{resource_type} with ID {resource_id} not found"

        final_details = details or {}
        final_details["resource_type"] = resource_type
        if resource_id:
            final_details["resource_id"] = resource_id

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.NOT_FOUND,
            message=message or default_message,
            details=final_details
        )


class DuplicateResourceException(APIException):
    """
    Raised when attempting to create a resource that already exists.

    Usage:
        raise DuplicateResourceException(
            resource_type="Business",
            field="website_url",
            value="https://example.com"
        )
    """

    def __init__(
        self,
        resource_type: str,
        field: Optional[str] = None,
        value: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        default_message = f"{resource_type} already exists"
        if field and value:
            default_message = f"{resource_type} with {field} '{value}' already exists"

        final_details = details or {}
        final_details["resource_type"] = resource_type
        if field:
            final_details["field"] = field
        if value:
            final_details["value"] = value

        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.DUPLICATE_RESOURCE,
            message=message or default_message,
            details=final_details
        )


class UnauthorizedException(APIException):
    """
    Raised when authentication fails or credentials are invalid.

    Usage:
        raise UnauthorizedException(message="Invalid credentials")
    """

    def __init__(
        self,
        message: str = "Authentication required",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=ErrorCode.UNAUTHORIZED,
            message=message,
            details=details
        )


class ForbiddenException(APIException):
    """
    Raised when user is authenticated but lacks permission.

    Usage:
        raise ForbiddenException(
            message="You do not have permission to delete this business"
        )
    """

    def __init__(
        self,
        message: str = "You do not have permission to perform this action",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=ErrorCode.FORBIDDEN,
            message=message,
            details=details
        )


class ValidationException(APIException):
    """
    Raised for custom validation errors beyond Pydantic validation.

    Usage:
        raise ValidationException(
            message="Invalid score range",
            details={"score_min": 80, "score_max": 60}
        )
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        final_details = details or {}
        if field:
            final_details["field"] = field

        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code=ErrorCode.VALIDATION_ERROR,
            message=message,
            details=final_details
        )


class DatabaseException(APIException):
    """
    Raised when database operations fail.

    Usage:
        raise DatabaseException(
            message="Failed to connect to database",
            details={"error": str(e)}
        )
    """

    def __init__(
        self,
        message: str = "Database operation failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.DATABASE_ERROR,
            message=message,
            details=details
        )


class InternalServerException(APIException):
    """
    Raised for unexpected internal server errors.

    Usage:
        raise InternalServerException(
            message="An unexpected error occurred",
            details={"error": str(e)}
        )
    """

    def __init__(
        self,
        message: str = "An internal server error occurred",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.INTERNAL_ERROR,
            message=message,
            details=details
        )


class RateLimitExceededException(APIException):
    """
    Raised when rate limit is exceeded.

    Usage:
        raise RateLimitExceededException(
            message="Too many requests",
            details={"retry_after": 60}
        )
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        final_details = details or {}
        if retry_after:
            final_details["retry_after"] = retry_after

        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            message=message,
            details=final_details
        )


class ServiceUnavailableException(APIException):
    """
    Raised when a required service is unavailable.

    Usage:
        raise ServiceUnavailableException(
            message="Database connection unavailable",
            details={"service": "PostgreSQL"}
        )
    """

    def __init__(
        self,
        message: str = "Service temporarily unavailable",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code=ErrorCode.SERVICE_UNAVAILABLE,
            message=message,
            details=details
        )
