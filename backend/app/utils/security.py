"""Security utilities for authentication and authorization"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uuid

from app.config import settings
from app.database import get_db
from app.models import User


# HTTP Bearer token scheme for OAuth2
security = HTTPBearer()

# Initialize Argon2 password hasher with secure defaults
# Using Argon2id variant (hybrid of Argon2i and Argon2d for best security)
password_hasher = PasswordHasher(
    time_cost=2,        # Number of iterations
    memory_cost=65536,  # Memory usage in KiB (64 MB)
    parallelism=1,      # Number of parallel threads
    hash_len=32,        # Length of the hash in bytes
    salt_len=16         # Length of the salt in bytes
)


def hash_password(password: str) -> str:
    """
    Hash a plain password using Argon2id.

    Args:
        password: Plain text password (minimum 8 characters)

    Returns:
        str: Argon2 hashed password

    Security Notes:
        - Uses Argon2id (hybrid algorithm, best security)
        - No password length limits (unlike bcrypt's 72-byte limit)
        - Memory-hard algorithm resistant to GPU/ASIC attacks
        - Never log or return plain passwords
        - Always validate password strength before hashing
    """
    # Hash password using Argon2
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against an Argon2 hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Argon2 hashed password from database

    Returns:
        bool: True if password matches, False otherwise

    Security Notes:
        - Constant-time comparison (Argon2 handles this)
        - Does not reveal whether password or hash is invalid
        - Automatically handles hash format validation
    """
    try:
        # Verify password - raises exception if mismatch
        password_hasher.verify(hashed_password, plain_password)
        return True
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        # Password doesn't match or hash is invalid
        return False


def validate_password_strength(password: str) -> bool:
    """
    Validate password meets minimum strength requirements.

    Current requirements:
    - Minimum 8 characters

    Args:
        password: Plain text password to validate

    Returns:
        bool: True if password meets requirements

    Future Enhancements:
        - Add complexity requirements (uppercase, lowercase, numbers, symbols)
        - Check against common password lists
        - Implement password history checking
    """
    return len(password) >= 8


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload data to encode (should include user_id, email)
        expires_delta: Optional expiration time delta (default: 24 hours from settings)

    Returns:
        str: Encoded JWT token

    Token Payload:
        - sub: Subject (user_id)
        - email: User email
        - exp: Expiration timestamp
        - iat: Issued at timestamp
        - type: Token type ("access")

    Security Notes:
        - Token signed with JWT_SECRET from settings
        - Uses HS256 algorithm
        - Include minimal data in payload
        - Validate expiration on every request
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any]
) -> str:
    """
    Create a JWT refresh token with longer expiration.

    Args:
        data: Payload data to encode (should include user_id, email)

    Returns:
        str: Encoded JWT refresh token

    Token Payload:
        - sub: Subject (user_id)
        - email: User email
        - exp: Expiration timestamp (7 days)
        - iat: Issued at timestamp
        - type: Token type ("refresh")

    Security Notes:
        - Refresh tokens have longer expiration (7 days)
        - Can only be used to generate new access tokens
        - Should be stored securely by client
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string

    Returns:
        dict: Decoded token payload

    Raises:
        HTTPException: If token is invalid, expired, or malformed

    Validates:
        - Token signature
        - Token expiration
        - Token type (must be "access")
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Validate token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def decode_refresh_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT refresh token.

    Args:
        token: JWT refresh token string

    Returns:
        dict: Decoded token payload

    Raises:
        HTTPException: If token is invalid, expired, or malformed

    Validates:
        - Token signature
        - Token expiration
        - Token type (must be "refresh")
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Validate token type
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type - expected refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate refresh token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Authentication dependency for protected routes.

    Extracts and validates JWT token from Authorization header,
    then retrieves the authenticated user from database.

    Args:
        credentials: HTTP Bearer credentials from Authorization header
        db: Database session

    Returns:
        User: Authenticated user object

    Raises:
        HTTPException: If token is invalid or user not found

    Usage:
        ```python
        @router.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.id, "email": current_user.email}
        ```

    Security Notes:
        - Validates token signature and expiration
        - Checks user exists and is active
        - Raises 401 for any authentication failures
        - Does not reveal whether token or user is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Extract token from credentials
        token = credentials.credentials

        # Decode and validate token
        payload = decode_access_token(token)

        # Extract user_id from token payload
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception

        # Convert string UUID to UUID object
        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            raise credentials_exception

    except HTTPException:
        raise credentials_exception

    # Query user from database
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise credentials_exception

    # Check if user account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user
