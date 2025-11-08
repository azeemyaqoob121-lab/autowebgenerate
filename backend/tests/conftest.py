"""Pytest Configuration and Shared Fixtures"""
import pytest
import uuid
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, Dict

from app.main import create_app
from app.database import Base, get_db
from app.config import Settings
from app.models import User, Business
from app.utils.security import hash_password, create_access_token


# Test database URL (PostgreSQL test database)
# Uses separate test database to avoid conflicts with development data
TEST_DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/autoweb_test_db"


@pytest.fixture(scope="function")
def test_db():
    """
    Create a fresh test database for each test function.

    Uses PostgreSQL test database for realistic testing.
    Creates all tables before test and drops them after.
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )
    Base.metadata.create_all(engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    yield TestingSessionLocal

    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_settings():
    """
    Create test-specific settings configuration.

    Returns Settings instance with test-appropriate values:
    - Test environment
    - Debug mode enabled
    - PostgreSQL test database URL
    - Test-specific JWT secret
    """
    return Settings(
        APP_NAME="AutoWeb Outreach AI API (Test)",
        API_VERSION="0.1.0-test",
        ENVIRONMENT="test",
        DEBUG=True,
        LOG_LEVEL="DEBUG",
        DATABASE_URL=TEST_DATABASE_URL,
        JWT_SECRET="test-secret-key",
        CORS_ORIGINS=["http://localhost:3000", "http://testserver"],
    )


@pytest.fixture(scope="function")
def app(test_db, test_settings):
    """
    Create FastAPI app instance for testing.

    Uses test settings and overrides database dependency
    to use in-memory test database.

    Args:
        test_db: Test database session factory
        test_settings: Test configuration settings

    Returns:
        FastAPI: Configured test application instance
    """
    # Create app with test settings
    test_app = create_app(config_override=test_settings)

    # Override database dependency to use test database
    def override_get_db():
        db = test_db()
        try:
            yield db
        finally:
            db.close()

    test_app.dependency_overrides[get_db] = override_get_db

    return test_app


@pytest.fixture(scope="function")
def client(app) -> Generator:
    """
    Create FastAPI test client.

    Provides TestClient instance for making HTTP requests to the app.
    Automatically handles startup/shutdown events.

    Args:
        app: FastAPI application instance

    Returns:
        TestClient: Client for making test requests

    Example:
        ```python
        def test_endpoint(client):
            response = client.get("/api/health")
            assert response.status_code == 200
        ```
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def db_session(test_db) -> Generator[Session, None, None]:
    """
    Create a database session for direct database operations in tests.

    Yields:
        Session: SQLAlchemy session for database operations

    Example:
        ```python
        def test_create_user(db_session):
            user = User(email="test@example.com", ...)
            db_session.add(user)
            db_session.commit()
            assert db_session.query(User).count() == 1
        ```
    """
    session = test_db()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def test_user(db_session: Session) -> User:
    """
    Create a test user in the database.

    Returns:
        User: Test user with email "test@example.com" and password "testpassword123"

    Example:
        ```python
        def test_user_login(client, test_user):
            response = client.post("/api/auth/login", json={
                "email": "test@example.com",
                "password": "testpassword123"
            })
            assert response.status_code == 200
        ```
    """
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        hashed_password=hash_password("testpassword123"),
        is_active=True,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_user_2(db_session: Session) -> User:
    """
    Create a second test user for multi-user testing scenarios.

    Returns:
        User: Test user with email "test2@example.com" and password "testpassword123"
    """
    user = User(
        id=uuid.uuid4(),
        email="test2@example.com",
        hashed_password=hash_password("testpassword123"),
        is_active=True,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_token(test_user: User) -> str:
    """
    Generate an authentication token for the test user.

    Returns:
        str: JWT access token

    Example:
        ```python
        def test_protected_endpoint(client, auth_token):
            headers = {"Authorization": f"Bearer {auth_token}"}
            response = client.get("/api/businesses", headers=headers)
            assert response.status_code == 200
        ```
    """
    token = create_access_token(data={"sub": test_user.email})
    return token


@pytest.fixture(scope="function")
def auth_headers(auth_token: str) -> Dict[str, str]:
    """
    Generate authentication headers for API requests.

    Returns:
        dict: Headers with Authorization bearer token

    Example:
        ```python
        def test_protected_endpoint(client, auth_headers):
            response = client.get("/api/businesses", headers=auth_headers)
            assert response.status_code == 200
        ```
    """
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="function")
def test_business(db_session: Session) -> Business:
    """
    Create a test business in the database.

    Returns:
        Business: Test business with realistic UK business data

    Example:
        ```python
        def test_get_business(client, auth_headers, test_business):
            response = client.get(f"/api/businesses/{test_business.id}", headers=auth_headers)
            assert response.status_code == 200
            assert response.json()["name"] == "Test Plumbing Services"
        ```
    """
    business = Business(
        id=uuid.uuid4(),
        name="Test Plumbing Services",
        email="contact@testplumbing.co.uk",
        phone="020 1234 5678",
        address="123 Test Street, London, W1A 1AA",
        website_url="https://www.testplumbing.co.uk",
        category="Plumbing",
        description="Professional plumbing services in London",
        location="London",
        score=85,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(business)
    db_session.commit()
    db_session.refresh(business)
    return business


@pytest.fixture(scope="function")
def test_businesses(db_session: Session):
    """
    Create multiple test businesses for list/filter testing.

    Returns:
        list[Business]: List of 5 test businesses with varied attributes

    Example:
        ```python
        def test_filter_by_location(client, auth_headers, test_businesses):
            response = client.get("/api/businesses?location=London", headers=auth_headers)
            assert response.status_code == 200
            london_businesses = [b for b in response.json()["items"] if b["location"] == "London"]
            assert len(london_businesses) == 2
        ```
    """
    businesses = [
        Business(
            id=uuid.uuid4(),
            name="London Plumbing Services",
            email="contact@londonplumbing.co.uk",
            phone="020 1111 1111",
            address="10 High Street, London, W1A 1AA",
            website_url="https://www.londonplumbing.co.uk",
            category="Plumbing",
            description="Expert plumbing in London",
            location="London",
            score=90,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        Business(
            id=uuid.uuid4(),
            name="Manchester Electrical",
            email="contact@manchesterelectrical.co.uk",
            phone="0161 2222 2222",
            address="20 Market Street, Manchester, M1 1AA",
            website_url="https://www.manchesterelectrical.co.uk",
            category="Electrical",
            description="Professional electrical services",
            location="Manchester",
            score=75,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        Business(
            id=uuid.uuid4(),
            name="Birmingham Construction",
            email="contact@birminghamconstruction.co.uk",
            phone="0121 3333 3333",
            address="30 Church Road, Birmingham, B1 1AA",
            website_url="https://www.birminghamconstruction.co.uk",
            category="Construction",
            description="Quality construction services",
            location="Birmingham",
            score=60,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        Business(
            id=uuid.uuid4(),
            name="Leeds Plumbing Ltd",
            email="contact@leedsplumbing.co.uk",
            phone="0113 4444 4444",
            address="40 Station Road, Leeds, LS1 1AA",
            website_url="https://www.leedsplumbing.co.uk",
            category="Plumbing",
            description="Reliable plumbing solutions",
            location="Leeds",
            score=85,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        Business(
            id=uuid.uuid4(),
            name="London Electrical Services",
            email="contact@londonelectrical.co.uk",
            phone="020 5555 5555",
            address="50 Main Street, London, W2 2BB",
            website_url="https://www.londonelectrical.co.uk",
            category="Electrical",
            description="Expert electrical contractors",
            location="London",
            score=95,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
    ]

    for business in businesses:
        db_session.add(business)
    db_session.commit()

    # Refresh all businesses
    for business in businesses:
        db_session.refresh(business)

    return businesses
