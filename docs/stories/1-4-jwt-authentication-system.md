# Story 1.4: JWT Authentication System

Status: todo

## Story

As a backend developer,
I want to implement JWT-based authentication,
So that API endpoints can be secured and users can be identified.

## Acceptance Criteria

1. User model created with fields: id, email, hashed_password, is_active, created_at
2. Password hashing utility implemented using bcrypt
3. JWT token generation and validation functions created
4. POST /api/auth/register endpoint created (accepts email, password)
5. POST /api/auth/login endpoint created (returns access token)
6. Authentication dependency created for protected routes
7. Token expiration set to 24 hours with refresh token support
8. Successful login returns valid JWT that can be validated

## Tasks / Subtasks

- [ ] Create User model (AC: 1)
  - [ ] Define `User` class in `backend/app/models/user.py` inheriting from SQLAlchemy Base
  - [ ] Add fields: id (UUID primary key), email (String, unique), hashed_password (String)
  - [ ] Add fields: is_active (Boolean, default True), created_at (DateTime)
  - [ ] Add index on email for fast lookups
  - [ ] Add relationship to scraping_jobs (will be created in Epic 2)
  - [ ] Export User model from `backend/app/models/__init__.py`

- [ ] Create Alembic migration for User table
  - [ ] Generate migration: `alembic revision --autogenerate -m "add_user_table"`
  - [ ] Review migration file for accuracy
  - [ ] Apply migration: `alembic upgrade head`
  - [ ] Verify user table created in PostgreSQL

- [ ] Implement password hashing utilities (AC: 2)
  - [ ] Create `backend/app/utils/security.py` module
  - [ ] Implement `hash_password(password: str) -> str` using bcrypt
  - [ ] Implement `verify_password(plain_password: str, hashed_password: str) -> bool`
  - [ ] Set bcrypt cost factor to 12 for security
  - [ ] Add password strength validation (minimum 8 characters)
  - [ ] Write unit tests for password hashing functions

- [ ] Implement JWT token utilities (AC: 3, 7)
  - [ ] Add JWT functions to `backend/app/utils/security.py`
  - [ ] Implement `create_access_token(data: dict, expires_delta: Optional[timedelta]) -> str`
  - [ ] Implement `decode_access_token(token: str) -> dict` with error handling
  - [ ] Use settings.JWT_SECRET and settings.JWT_ALGORITHM from config
  - [ ] Set default expiration to 24 hours (configurable via settings.ACCESS_TOKEN_EXPIRE_MINUTES)
  - [ ] Add refresh token generation function (longer expiration: 7 days)
  - [ ] Write unit tests for JWT functions

- [ ] Create Pydantic schemas for authentication (AC: 4, 5)
  - [ ] Create `backend/app/schemas/auth.py` module
  - [ ] Define `UserRegister` schema: email (EmailStr), password (str, min_length=8)
  - [ ] Define `UserLogin` schema: email (EmailStr), password (str)
  - [ ] Define `Token` response schema: access_token (str), token_type (str), refresh_token (Optional[str])
  - [ ] Define `TokenData` schema for decoded token: user_id (UUID), email (str)
  - [ ] Add password confirmation field to UserRegister with validator

- [ ] Implement registration endpoint (AC: 4)
  - [ ] Create `backend/app/routes/auth.py` router
  - [ ] Implement POST /api/auth/register endpoint
  - [ ] Validate email not already registered (check User table)
  - [ ] Hash password using security utilities
  - [ ] Create new User record in database
  - [ ] Return success response with user_id (do NOT return token on registration)
  - [ ] Handle duplicate email error with 400 Bad Request
  - [ ] Write integration tests for registration endpoint

- [ ] Implement login endpoint (AC: 5, 8)
  - [ ] Implement POST /api/auth/login endpoint in auth router
  - [ ] Query User by email from database
  - [ ] Verify password using verify_password utility
  - [ ] Generate access token with user_id and email in payload
  - [ ] Generate refresh token
  - [ ] Return Token response with access_token, refresh_token, token_type="bearer"
  - [ ] Return 401 Unauthorized for invalid credentials
  - [ ] Write integration tests for login endpoint (success and failure cases)

- [ ] Create authentication dependency (AC: 6)
  - [ ] Implement `get_current_user()` dependency in `backend/app/utils/security.py`
  - [ ] Extract Bearer token from Authorization header
  - [ ] Decode and validate JWT token
  - [ ] Query User from database using token payload user_id
  - [ ] Raise HTTPException 401 if token invalid or user not found
  - [ ] Check user.is_active flag, reject inactive users
  - [ ] Return User object for use in protected route handlers

- [ ] Add refresh token endpoint (AC: 7)
  - [ ] Implement POST /api/auth/refresh endpoint
  - [ ] Accept refresh_token in request body
  - [ ] Validate refresh token (different secret or flag in payload)
  - [ ] Generate new access token
  - [ ] Return new Token response
  - [ ] Write tests for token refresh flow

- [ ] Register auth router in main application
  - [ ] Import auth router in `backend/app/main.py`
  - [ ] Include router: `app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])`
  - [ ] Verify endpoints appear in /docs Swagger UI
  - [ ] Test complete authentication flow manually

- [ ] Write comprehensive test suite
  - [ ] Create `backend/tests/test_auth.py`
  - [ ] Test user registration (success, duplicate email, weak password)
  - [ ] Test login (success, wrong password, non-existent user)
  - [ ] Test token validation and expiration
  - [ ] Test get_current_user dependency
  - [ ] Test protected endpoint with valid/invalid/expired tokens
  - [ ] Test refresh token flow
  - [ ] All tests should pass

## Dev Notes

### Learnings from Previous Stories

**From Story 1.3 (Status: review)**
- **Database Session Management**: Use `get_db()` dependency from `backend/app/database.py` in all route handlers
- **Settings Configuration**: JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES already configured in `backend/app/config.py`
- **Application Factory**: Use `create_app()` in tests to create app instances with test configuration
- **Test Fixtures**: Leverage fixtures from `backend/tests/conftest.py` (test_db, test_settings, app, client)
- **Dependencies Installation**: May need to resolve psycopg2-binary Windows issue before running tests

**From Story 1.2 (Status: review)**
- **Model Patterns**: Follow same patterns as Business, Evaluation models (UUID pk, timestamps, indexes)
- **Alembic Migrations**: Use `alembic revision --autogenerate` for new models
- **Test Database**: Tests use SQLite in-memory database from conftest.py fixtures

[Source: stories/1-3-fastapi-application-foundation.md#Dev-Agent-Record]

### Project Structure

```
backend/app/
├── models/
│   ├── user.py          # NEW: User model
│   └── __init__.py      # UPDATE: Export User
├── routes/
│   ├── auth.py          # NEW: Authentication endpoints
│   └── __init__.py
├── schemas/
│   ├── auth.py          # NEW: Auth request/response schemas
│   └── __init__.py
├── utils/
│   ├── security.py      # NEW: Password hashing, JWT utilities, auth dependency
│   └── __init__.py      # NEW: Create utils package
└── main.py              # UPDATE: Include auth router
```

### Technical Constraints

- **JWT Library**: python-jose[cryptography] (already in requirements.txt)
- **Password Hashing**: passlib with bcrypt backend (already in requirements.txt)
- **Token Expiration**: 24 hours access token, 7 days refresh token (configurable)
- **Password Requirements**: Minimum 8 characters, consider adding complexity requirements
- **Token Storage**: Client-side (localStorage or httpOnly cookies - frontend decision)

### Security Best Practices

**Password Hashing:**
- Use bcrypt with cost factor 12 (balance security and performance)
- Never log or return plain passwords
- Always validate password strength before hashing

**JWT Tokens:**
- Include minimal payload data (user_id, email, exp, iat)
- Use secure secret key (minimum 32 characters, random)
- Set appropriate expiration times
- Validate token signature and expiration on every request
- Consider token blacklist for logout (future enhancement)

**API Security:**
- Use HTTPS in production (terminate SSL at load balancer)
- Return generic error messages for authentication failures (don't reveal if email exists)
- Rate limit authentication endpoints (future enhancement)
- Log authentication attempts for security monitoring

### Authentication Flow

**Registration:**
1. User submits email + password
2. Validate email format and password strength
3. Check email not already registered
4. Hash password with bcrypt
5. Create User record
6. Return success (user must login separately)

**Login:**
1. User submits email + password
2. Query User by email
3. Verify hashed password matches
4. Generate JWT access token (24h expiration)
5. Generate JWT refresh token (7d expiration)
6. Return tokens

**Protected Route Access:**
1. Client includes token in Authorization: Bearer {token} header
2. get_current_user dependency extracts and validates token
3. User object injected into route handler
4. Route executes with authenticated user context

**Token Refresh:**
1. Client submits refresh token before access token expires
2. Validate refresh token
3. Generate new access token
4. Return new access token

### References

- [Source: docs/epics.md#Story-1.4]
- [Source: docs/PRD.md#FR019] (JWT-based authentication requirement)
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- python-jose: https://python-jose.readthedocs.io/
- passlib bcrypt: https://passlib.readthedocs.io/en/stable/lib/passlib.hash.bcrypt.html

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

- 2025-11-01: Story created from Epic 1, Story 4 in epics.md
