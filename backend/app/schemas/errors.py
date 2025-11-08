"""Error response schemas for standardized API error handling"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


# Error code constants
class ErrorCode:
    """Standard error codes used across the API"""
    # Validation errors (4xx)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    BUSINESS_NOT_FOUND = "BUSINESS_NOT_FOUND"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    DUPLICATE_RESOURCE = "DUPLICATE_RESOURCE"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # Server errors (5xx)
    DATABASE_ERROR = "DATABASE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


class ValidationFieldError(BaseModel):
    """Individual field validation error"""
    field: str = Field(..., description="Field name that failed validation")
    message: str = Field(..., description="Human-readable error message")

    class Config:
        json_schema_extra = {
            "example": {
                "field": "email",
                "message": "value is not a valid email address"
            }
        }


class ErrorDetail(BaseModel):
    """Detailed error information"""
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error context and debugging information"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "code": "BUSINESS_NOT_FOUND",
                "message": "Business with ID 123e4567-e89b-12d3-a456-426614174000 not found",
                "details": {
                    "business_id": "123e4567-e89b-12d3-a456-426614174000",
                    "timestamp": "2025-11-01T12:00:00Z",
                    "request_id": "abc-123-def-456"
                }
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response format for all API errors"""
    error: ErrorDetail = Field(..., description="Error details")

    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": {
                        "fields": [
                            {
                                "field": "email",
                                "message": "value is not a valid email address"
                            }
                        ],
                        "request_id": "abc-123-def-456"
                    }
                }
            }
        }


class ValidationErrorResponse(BaseModel):
    """Specialized error response for validation failures"""
    error: ErrorDetail = Field(..., description="Validation error details")

    @classmethod
    def from_validation_errors(
        cls,
        errors: List[Dict[str, Any]],
        request_id: Optional[str] = None
    ) -> "ValidationErrorResponse":
        """
        Create a validation error response from Pydantic validation errors.

        Args:
            errors: List of validation errors from Pydantic
            request_id: Optional request ID for tracking

        Returns:
            ValidationErrorResponse with formatted error details
        """
        field_errors = []

        for error in errors:
            # Extract field name from location tuple
            field_loc = error.get("loc", ())
            field_name = ".".join(str(loc) for loc in field_loc if loc != "body")

            field_errors.append({
                "field": field_name or "unknown",
                "message": error.get("msg", "Validation failed")
            })

        details = {"fields": field_errors}
        if request_id:
            details["request_id"] = request_id
            details["timestamp"] = datetime.utcnow().isoformat() + "Z"

        return cls(
            error=ErrorDetail(
                code=ErrorCode.VALIDATION_ERROR,
                message="Request validation failed",
                details=details
            )
        )

    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": {
                        "fields": [
                            {
                                "field": "email",
                                "message": "value is not a valid email address"
                            },
                            {
                                "field": "password",
                                "message": "ensure this value has at least 8 characters"
                            }
                        ],
                        "request_id": "abc-123-def-456",
                        "timestamp": "2025-11-01T12:00:00Z"
                    }
                }
            }
        }
