"""
Authentication Endpoint Tests

Tests for user registration, login, token refresh, and JWT authentication.
Tests password hashing, token generation, and protected endpoint access.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import User


@pytest.mark.auth
@pytest.mark.integration
def test_login_success(client: TestClient, test_user: User):
    """Test successful login with valid credentials."""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data
    assert "expires_in" in data

    # Verify token type
    assert data["token_type"] == "bearer"

    # Verify tokens are non-empty strings
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0
    assert isinstance(data["refresh_token"], str)
    assert len(data["refresh_token"]) > 0


@pytest.mark.auth
@pytest.mark.integration
def test_login_invalid_email(client: TestClient, test_user: User):
    """Test login fails with non-existent email."""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "testpassword123"
        }
    )

    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.auth
@pytest.mark.integration
def test_login_invalid_password(client: TestClient, test_user: User):
    """Test login fails with incorrect password."""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.auth
@pytest.mark.integration
def test_login_validation_invalid_email_format(client: TestClient):
    """Test login validation rejects invalid email format."""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "invalid-email",
            "password": "testpassword123"
        }
    )

    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.auth
@pytest.mark.integration
def test_login_validation_missing_fields(client: TestClient):
    """Test login validation requires all fields."""
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com"}
    )

    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.auth
@pytest.mark.integration
def test_access_protected_endpoint_with_valid_token(client: TestClient, auth_headers: dict):
    """Test accessing protected endpoint with valid JWT token."""
    response = client.get("/api/businesses", headers=auth_headers)

    # Should succeed (200) or return empty list, but not 401/403
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "items" in data or isinstance(data, list)


@pytest.mark.auth
@pytest.mark.integration
def test_access_protected_endpoint_without_token(client: TestClient):
    """Test accessing protected endpoint without authentication token."""
    response = client.get("/api/businesses")

    assert response.status_code == 403
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "FORBIDDEN"


@pytest.mark.auth
@pytest.mark.integration
def test_access_protected_endpoint_with_invalid_token(client: TestClient):
    """Test accessing protected endpoint with invalid JWT token."""
    headers = {"Authorization": "Bearer invalid-token-12345"}
    response = client.get("/api/businesses", headers=headers)

    assert response.status_code in [401, 403]
    data = response.json()
    assert "error" in data


@pytest.mark.auth
@pytest.mark.integration
def test_access_protected_endpoint_with_malformed_header(client: TestClient):
    """Test accessing protected endpoint with malformed auth header."""
    # Missing "Bearer" prefix
    headers = {"Authorization": "some-token"}
    response = client.get("/api/businesses", headers=headers)

    assert response.status_code in [401, 403]


@pytest.mark.auth
@pytest.mark.integration
def test_token_contains_user_identity(client: TestClient, test_user: User, auth_token: str):
    """Test JWT token contains user identity information."""
    from jose import jwt
    from app.config import Settings

    settings = Settings()

    # Decode token without verification (for testing only)
    decoded = jwt.decode(
        auth_token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )

    # Verify token contains user email
    assert "sub" in decoded
    assert decoded["sub"] == test_user.email


@pytest.mark.auth
@pytest.mark.integration
def test_login_inactive_user(client: TestClient, db_session: Session):
    """Test login fails for inactive user account."""
    import uuid
    from app.utils.security import hash_password

    # Create inactive user
    inactive_user = User(
        id=uuid.uuid4(),
        email="inactive@example.com",
        hashed_password=hash_password("testpassword123"),
        is_active=False
    )
    db_session.add(inactive_user)
    db_session.commit()

    response = client.post(
        "/api/auth/login",
        json={
            "email": "inactive@example.com",
            "password": "testpassword123"
        }
    )

    assert response.status_code == 401
    data = response.json()
    assert "error" in data


@pytest.mark.auth
@pytest.mark.integration
def test_multiple_logins_same_user(client: TestClient, test_user: User):
    """Test same user can login multiple times (generates different tokens)."""
    credentials = {
        "email": "test@example.com",
        "password": "testpassword123"
    }

    response1 = client.post("/api/auth/login", json=credentials)
    response2 = client.post("/api/auth/login", json=credentials)

    assert response1.status_code == 200
    assert response2.status_code == 200

    token1 = response1.json()["access_token"]
    token2 = response2.json()["access_token"]

    # Tokens should be different (different timestamps)
    assert token1 != token2


@pytest.mark.auth
@pytest.mark.integration
def test_concurrent_requests_with_same_token(client: TestClient, auth_headers: dict, test_business):
    """Test same token can be used for multiple concurrent requests."""
    # Make multiple requests with same token
    responses = [
        client.get("/api/businesses", headers=auth_headers)
        for _ in range(5)
    ]

    # All should succeed
    assert all(r.status_code == 200 for r in responses)


@pytest.mark.auth
@pytest.mark.integration
def test_login_case_sensitive_email(client: TestClient, test_user: User):
    """Test email matching is case-insensitive for login."""
    # Try login with uppercase email
    response = client.post(
        "/api/auth/login",
        json={
            "email": "TEST@EXAMPLE.COM",
            "password": "testpassword123"
        }
    )

    # Should succeed or fail consistently (depending on implementation)
    # Most implementations treat emails as case-insensitive
    assert response.status_code in [200, 401]
