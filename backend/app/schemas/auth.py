"""Authentication schemas for request/response validation"""
from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserRegister(BaseModel):
    """
    User registration request schema.

    Validates:
        - Email format
        - Password minimum length
        - Password confirmation match
    """
    email: EmailStr = Field(
        ...,
        description="User email address (must be unique)"
    )

    password: str = Field(
        ...,
        min_length=8,
        description="User password (minimum 8 characters)"
    )

    password_confirm: str = Field(
        ...,
        min_length=8,
        description="Password confirmation (must match password)"
    )

    @field_validator('password_confirm')
    @classmethod
    def passwords_match(cls, v, info):
        """Validate that password and password_confirm match"""
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
                "password_confirm": "securepassword123"
            }
        }


class UserLogin(BaseModel):
    """
    User login request schema.

    Validates:
        - Email format
        - Password provided
    """
    email: EmailStr = Field(
        ...,
        description="User email address"
    )

    password: str = Field(
        ...,
        description="User password"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }


class Token(BaseModel):
    """
    JWT token response schema.

    Returned on successful login or token refresh.
    """
    access_token: str = Field(
        ...,
        description="JWT access token (24 hour expiration)"
    )

    refresh_token: Optional[str] = Field(
        None,
        description="JWT refresh token (7 day expiration)"
    )

    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenData(BaseModel):
    """
    Decoded JWT token payload schema.

    Used internally for token validation.
    """
    user_id: UUID = Field(
        ...,
        description="User ID from token payload"
    )

    email: str = Field(
        ...,
        description="User email from token payload"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com"
            }
        }


class RefreshTokenRequest(BaseModel):
    """
    Refresh token request schema.

    Used to obtain a new access token using a refresh token.
    """
    refresh_token: str = Field(
        ...,
        description="JWT refresh token"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class UserResponse(BaseModel):
    """
    User response schema.

    Returned on successful registration or user profile queries.
    """
    id: UUID = Field(
        ...,
        description="User ID"
    )

    email: str = Field(
        ...,
        description="User email address"
    )

    is_active: bool = Field(
        ...,
        description="Account active status"
    )

    created_at: datetime = Field(
        ...,
        description="Account creation timestamp"
    )

    class Config:
        from_attributes = True  # Pydantic v2: allows ORM model to schema conversion
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "is_active": True,
                "created_at": "2025-11-01T12:00:00Z"
            }
        }


class RegisterResponse(BaseModel):
    """
    Registration success response schema.

    Returned on successful user registration.
    """
    message: str = Field(
        default="User registered successfully",
        description="Success message"
    )

    user: UserResponse = Field(
        ...,
        description="Created user details"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "User registered successfully",
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "is_active": True,
                    "created_at": "2025-11-01T12:00:00Z"
                }
            }
        }
