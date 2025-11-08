# Story 1.9: Backend Testing Framework Setup

Status: todo

## Story

As a backend developer,
I want a testing framework configured,
So that I can write and run automated tests for API endpoints.

## Acceptance Criteria

1. Pytest configured with FastAPI test client
2. Test database setup with automatic cleanup between tests
3. Factory fixtures created for generating test data (businesses, users)
4. Sample tests written for authentication endpoints (login, register)
5. Sample tests written for business CRUD endpoints
6. Test coverage reporting configured
7. All tests pass successfully
8. GitHub Actions or CI pipeline configured to run tests on push

## Tasks / Subtasks

- [ ] Verify pytest configuration (AC: 1)
  - [ ] Confirm pytest and pytest-asyncio in requirements.txt (already added in Story 1.1)
  - [ ] Create `backend/pytest.ini` configuration file
  - [ ] Configure test discovery patterns (test_*.py, *_test.py)
  - [ ] Set asyncio mode to "auto" for async test support
  - [ ] Configure test output verbosity and formatting
  - [ ] Add markers for test categorization (unit, integration, slow)

- [ ] Enhance test fixtures in conftest.py (AC: 2)
  - [ ] Review existing fixtures from Story 1.3 (test_db, test_settings, app, client)
  - [ ] Enhance test_db fixture to use transaction rollback (faster than recreating tables)
  - [ ] Add fixture for async database sessions (if using async SQLAlchemy)
  - [ ] Add fixture to reset database to clean state between tests
  - [ ] Add fixture for Redis test client (separate Redis DB for tests)
  - [ ] Ensure fixtures have proper scope (function, session, module)

- [ ] Create factory fixtures for test data (AC: 3)
  - [ ] Install factory_boy: Add to requirements.txt
  - [ ] Create `backend/tests/factories.py` module
  - [ ] Implement UserFactory for creating test users
  - [ ] Implement BusinessFactory for creating test businesses
  - [ ] Implement EvaluationFactory for creating test evaluations
  - [ ] Implement TemplateFactory for creating test templates
  - [ ] Add faker integration for realistic test data
  - [ ] Add factory fixtures to conftest.py

- [ ] Create authentication helper fixtures
  - [ ] Create fixture `auth_headers()` that returns valid JWT token headers
  - [ ] Create fixture `authenticated_user()` that creates user and returns token
  - [ ] Create fixture `authenticated_client()` that returns TestClient with auth headers
  - [ ] Support multiple user roles if needed (admin, regular user)
  - [ ] Add fixture to generate expired tokens for testing token expiration

- [ ] Write comprehensive auth tests (AC: 4)
  - [ ] Verify `backend/tests/test_auth.py` exists (should be created in Story 1.4)
  - [ ] Ensure tests cover: registration (success, duplicate email, weak password)
  - [ ] Ensure tests cover: login (success, wrong password, non-existent user, inactive user)
  - [ ] Ensure tests cover: token validation (valid, invalid, expired, malformed)
  - [ ] Ensure tests cover: protected endpoint access (with/without token)
  - [ ] Ensure tests cover: refresh token flow
  - [ ] All auth tests should pass

- [ ] Write comprehensive business CRUD tests (AC: 5)
  - [ ] Verify `backend/tests/test_businesses.py` exists (should be created in Story 1.5)
  - [ ] Ensure tests cover: List businesses (pagination, filtering, sorting)
  - [ ] Ensure tests cover: Get business by ID (found, not found)
  - [ ] Ensure tests cover: Create business (success, duplicate website, validation errors)
  - [ ] Ensure tests cover: Update business (success, not found, duplicate website)
  - [ ] Ensure tests cover: Delete business (soft delete, not found)
  - [ ] Ensure tests cover: Text search functionality
  - [ ] Ensure tests cover: Authentication required (401 without token)
  - [ ] All business tests should pass

- [ ] Configure test coverage reporting (AC: 6)
  - [ ] Install pytest-cov: Add to requirements.txt
  - [ ] Configure coverage in pytest.ini or .coveragerc
  - [ ] Set coverage source to app/ directory
  - [ ] Exclude test files, migrations, __init__.py from coverage
  - [ ] Generate HTML coverage report
  - [ ] Set minimum coverage threshold (target: 80%)
  - [ ] Run coverage report: `pytest --cov=app --cov-report=html`

- [ ] Create test database management script
  - [ ] Create `backend/scripts/setup_test_db.py`
  - [ ] Script creates separate test database
  - [ ] Script runs Alembic migrations on test database
  - [ ] Script can reset test database to clean state
  - [ ] Document usage in README

- [ ] Configure CI/CD pipeline (AC: 8)
  - [ ] Create `.github/workflows/backend-tests.yml`
  - [ ] Configure workflow to trigger on push and pull request
  - [ ] Setup PostgreSQL service container for tests
  - [ ] Setup Redis service container for tests
  - [ ] Install Python dependencies
  - [ ] Run Alembic migrations in CI
  - [ ] Run pytest with coverage
  - [ ] Upload coverage report to Codecov or similar (optional)
  - [ ] Configure branch protection requiring passing tests

- [ ] Write test for error handling (from Story 1.6)
  - [ ] Create `backend/tests/test_error_handling.py` if not exists
  - [ ] Test 404 responses return correct error format
  - [ ] Test 400 validation errors return correct format
  - [ ] Test 422 Pydantic validation errors
  - [ ] Test 401 unauthorized responses
  - [ ] Test 500 internal error handling
  - [ ] Test 429 rate limiting responses
  - [ ] All error handling tests pass

- [ ] Add test utilities module
  - [ ] Create `backend/tests/utils.py`
  - [ ] Add helper: `create_test_business()` - shorthand for factory
  - [ ] Add helper: `create_test_user()` - shorthand for user factory
  - [ ] Add helper: `get_auth_token(user)` - generate JWT for user
  - [ ] Add helper: `assert_error_response(response, status_code, error_code)` - validate error format
  - [ ] Add helper: `load_fixture_data(filename)` - load JSON test fixtures

- [ ] Verify all tests pass (AC: 7)
  - [ ] Run full test suite: `pytest backend/tests/ -v`
  - [ ] Verify 0 failures
  - [ ] Fix any failing tests from previous stories
  - [ ] Run with coverage: `pytest --cov=app --cov-report=term-missing`
  - [ ] Ensure coverage meets minimum threshold (>80%)
  - [ ] Document test running instructions in README

- [ ] Document testing practices
  - [ ] Create `docs/testing-guide.md`
  - [ ] Document how to run tests locally
  - [ ] Explain test fixtures and factories
  - [ ] Provide examples of writing new tests
  - [ ] Document testing best practices (AAA pattern, test isolation, naming)
  - [ ] Explain CI/CD pipeline and coverage requirements

## Dev Notes

### Learnings from Previous Stories

**From Story 1.3 (Status: review)**
- **Test Fixtures**: `backend/tests/conftest.py` already has test_db, test_settings, app, client fixtures
- **Test Database**: Currently uses SQLite in-memory, works well for unit tests
- **TestClient**: FastAPI TestClient from starlette.testclient

**From Story 1.2 (Status: review)**
- **Model Tests**: `backend/tests/test_models.py` already created with comprehensive model tests
- **All model tests pass**: Relationship, cascade delete, constraint validation covered

**Previous Story Test Examples:**
- Story 1.2: Comprehensive model tests (test_models.py)
- Story 1.3: Application initialization tests (test_app.py)
- Story 1.4: Authentication tests (test_auth.py) - to be created
- Story 1.5: Business CRUD tests (test_businesses.py) - to be created
- Story 1.6: Error handling tests (test_error_handling.py) - to be created

[Source: stories/1-2-postgresql-database-schema-and-models.md#Dev-Agent-Record]

### Project Structure

```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # UPDATE: Enhance fixtures
│   ├── factories.py         # NEW: Factory Boy factories
│   ├── utils.py             # NEW: Test helper functions
│   ├── test_models.py       # EXISTS: From Story 1.2
│   ├── test_app.py          # EXISTS: From Story 1.3
│   ├── test_auth.py         # CREATE: In Story 1.4
│   ├── test_businesses.py   # CREATE: In Story 1.5
│   └── test_error_handling.py  # CREATE: In Story 1.6
├── scripts/
│   └── setup_test_db.py     # NEW: Test DB management
├── pytest.ini               # NEW: Pytest configuration
└── .coveragerc              # NEW: Coverage configuration

.github/
└── workflows/
    └── backend-tests.yml    # NEW: CI/CD pipeline
```

### Technical Constraints

- **Pytest Version**: 7.4.4 (from requirements.txt)
- **Test Isolation**: Each test should be independent, no shared state
- **Database**: Use SQLite for fast unit tests, PostgreSQL for integration tests (CI)
- **Coverage Target**: Minimum 80% code coverage
- **Test Speed**: Unit tests <10s total, integration tests <60s total

### Testing Philosophy

**Test Types:**
1. **Unit Tests**: Test individual functions/methods in isolation
2. **Integration Tests**: Test API endpoints with database
3. **Functional Tests**: Test complete user workflows

**Test Organization:**
- Group related tests in classes (TestAuth, TestBusinessCRUD)
- Use descriptive test names (test_create_business_with_valid_data)
- Follow AAA pattern: Arrange, Act, Assert
- One assertion per test (prefer multiple specific tests over one complex test)

**Test Fixtures:**
- Use fixtures for test data setup
- Keep fixtures small and focused
- Use factories for creating test data with random values
- Clean up after tests (rollback transactions, clear Redis)

### Factory Boy Patterns

**Basic Factory:**
```python
import factory
from factory.alchemy import SQLAlchemyModelFactory
from app.models import Business, User
from tests.conftest import test_db

class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = test_db
        sqlalchemy_session_persistence = "commit"

    id = factory.Faker("uuid4")
    email = factory.Faker("email")
    hashed_password = factory.LazyFunction(lambda: hash_password("password123"))
    is_active = True
    created_at = factory.Faker("date_time_this_year")

class BusinessFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Business
        sqlalchemy_session = test_db
        sqlalchemy_session_persistence = "commit"

    id = factory.Faker("uuid4")
    name = factory.Faker("company")
    email = factory.Faker("company_email")
    phone = factory.Faker("phone_number")
    address = factory.Faker("address")
    website_url = factory.Faker("url")
    category = factory.Faker("random_element", elements=["Plumbing", "Electrician", "Builder"])
    description = factory.Faker("text", max_nb_chars=200)
    location = factory.Faker("city")
    score = factory.Faker("random_int", min=0, max=100)
```

**Usage in Tests:**
```python
def test_create_business():
    business = BusinessFactory.create(name="Test Business", score=45)
    assert business.id is not None
    assert business.name == "Test Business"
    assert business.score == 45
```

### Pytest Configuration

**pytest.ini:**
```ini
[pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --tb=short
    --disable-warnings
markers =
    unit: Unit tests (fast, no external dependencies)
    integration: Integration tests (database, API)
    slow: Slow tests (may take >5 seconds)
    auth: Authentication related tests
    crud: CRUD operation tests
asyncio_mode = auto
```

**.coveragerc:**
```ini
[run]
source = app
omit =
    */tests/*
    */migrations/*
    */__init__.py
    */conftest.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
precision = 2
skip_covered = False
skip_empty = True

[html]
directory = htmlcov
```

### CI/CD Pipeline Configuration

**GitHub Actions Workflow:**
```yaml
name: Backend Tests

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'backend/**'
  pull_request:
    branches: [ main, develop ]
    paths:
      - 'backend/**'

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: autoweb_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run migrations
        run: |
          cd backend
          alembic upgrade head
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/autoweb_test

      - name: Run tests with coverage
        run: |
          cd backend
          pytest --cov=app --cov-report=xml --cov-report=term-missing
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/autoweb_test
          REDIS_URL: redis://localhost:6379/0
          JWT_SECRET: test-secret-key-for-ci
          ENVIRONMENT: test

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml
          flags: backend
          fail_ci_if_error: false
```

### Test Example Patterns

**Authentication Test:**
```python
def test_register_user_success(client):
    response = client.post("/api/auth/register", json={
        "email": "newuser@example.com",
        "password": "SecurePass123!"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data

def test_login_with_valid_credentials(client, authenticated_user):
    email, password = "user@example.com", "password123"
    UserFactory.create(email=email, hashed_password=hash_password(password))

    response = client.post("/api/auth/login", json={
        "email": email,
        "password": password
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
```

**CRUD Test:**
```python
def test_create_business_with_auth(authenticated_client):
    business_data = {
        "name": "Test Business",
        "email": "test@business.com",
        "website_url": "https://testbusiness.com",
        "category": "Plumbing",
        "location": "Manchester"
    }
    response = authenticated_client.post("/api/businesses", json=business_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Business"
    assert "id" in data

def test_create_business_without_auth(client):
    response = client.post("/api/businesses", json={"name": "Test"})
    assert response.status_code == 401
```

### References

- [Source: docs/epics.md#Story-1.9]
- [Source: docs/PRD.md#NFR005] (Testing as part of quality assurance)
- Pytest Documentation: https://docs.pytest.org/
- FastAPI Testing: https://fastapi.tiangolo.com/tutorial/testing/
- Factory Boy: https://factoryboy.readthedocs.io/
- pytest-cov: https://pytest-cov.readthedocs.io/

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

<!-- Will be filled during implementation -->

### Debug Log References

<!-- Will be filled during implementation -->

### Completion Notes List

<!-- Will be filled during implementation -->

### File List

<!-- Will be filled during implementation -->

## Change Log

- 2025-11-01: Story created from Epic 1, Story 9 in epics.md
