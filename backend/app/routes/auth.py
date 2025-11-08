"""Authentication API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import uuid

from app.database import get_db
from app.models import User
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    Token,
    RefreshTokenRequest,
    RegisterResponse,
    UserResponse
)
from app.utils.security import (
    hash_password,
    verify_password,
    validate_password_strength,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_current_user
)

router = APIRouter()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password. Email must be unique.",
    responses={
        201: {
            "description": "User successfully registered",
            "content": {
                "application/json": {
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
            }
        },
        400: {
            "description": "Bad request - validation error or email already registered",
            "content": {
                "application/json": {
                    "examples": {
                        "duplicate_email": {
                            "summary": "Email already registered",
                            "value": {"detail": "Email already registered"}
                        },
                        "weak_password": {
                            "summary": "Weak password",
                            "value": {"detail": "Password must be at least 8 characters long"}
                        }
                    }
                }
            }
        }
    }
)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.

    - **email**: User's email address (must be unique)
    - **password**: User's password (minimum 8 characters)
    - **password_confirm**: Password confirmation (must match password)

    Returns the created user object (without password).

    Note: User must login separately after registration to obtain access token.
    """
    # Validate password strength
    if not validate_password_strength(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )

    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = hash_password(user_data.password)

    # Create new user
    new_user = User(
        id=uuid.uuid4(),
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=True
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Return success response
    return RegisterResponse(
        message="User registered successfully",
        user=UserResponse.from_orm(new_user)
    )


@router.post(
    "/login",
    response_model=Token,
    summary="Login user",
    description="Authenticate user and return access and refresh tokens.",
    responses={
        200: {
            "description": "Successfully authenticated",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "description": "Authentication failed - invalid credentials",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid credentials"}
                }
            }
        }
    }
)
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens.

    - **email**: User's email address
    - **password**: User's password

    Returns:
    - **access_token**: JWT token for API authentication (24 hour expiration)
    - **refresh_token**: JWT token for obtaining new access tokens (7 day expiration)
    - **token_type**: Token type (always "bearer")

    Use the access_token in subsequent requests with the Authorization header:
    `Authorization: Bearer {access_token}`
    """
    # Query user by email
    user = db.query(User).filter(User.email == user_credentials.email).first()

    # Validate user exists and password is correct
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Create access token
    access_token_data = {
        "sub": str(user.id),
        "email": user.email
    }
    access_token = create_access_token(data=access_token_data)

    # Create refresh token
    refresh_token = create_refresh_token(data=access_token_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token",
    description="Obtain a new access token using a refresh token.",
    responses={
        200: {
            "description": "Successfully refreshed token",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "description": "Invalid or expired refresh token",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate refresh token"}
                }
            }
        }
    }
)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using a refresh token.

    - **refresh_token**: Valid JWT refresh token

    Returns:
    - **access_token**: New JWT access token (24 hour expiration)
    - **token_type**: Token type (always "bearer")

    Note: The refresh token itself is not renewed. Use login to obtain a new refresh token.
    """
    # Decode and validate refresh token
    payload = decode_refresh_token(refresh_request.refresh_token)

    # Extract user_id from token
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Convert to UUID
    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user still exists and is active
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new access token
    access_token_data = {
        "sub": str(user.id),
        "email": user.email
    }
    access_token = create_access_token(data=access_token_data)

    return Token(
        access_token=access_token,
        token_type="bearer"
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get the authenticated user's profile information.",
    responses={
        200: {
            "description": "Current user profile",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "user@example.com",
                        "is_active": True,
                        "created_at": "2025-11-01T12:00:00Z"
                    }
                }
            }
        },
        401: {
            "description": "Not authenticated",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            }
        }
    }
)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get authenticated user's profile.

    Requires valid access token in Authorization header:
    `Authorization: Bearer {access_token}`

    Returns:
    - **id**: User ID
    - **email**: User email
    - **is_active**: Account active status
    - **created_at**: Account creation timestamp
    """
    return UserResponse.from_orm(current_user)
