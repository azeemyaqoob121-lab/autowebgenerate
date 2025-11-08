# Story 1.6: API Error Handling and Validation

Status: todo

## Story

As a backend developer,
I want comprehensive error handling and validation,
So that API consumers receive clear, actionable error messages.

## Acceptance Criteria

1. Custom exception handlers created for common error types (404, 400, 500, 401, 403)
2. Pydantic validation errors return structured, readable error responses
3. Database errors caught and transformed to appropriate HTTP responses
4. Request validation implemented on all endpoints using Pydantic models
5. Error responses follow consistent format: {"error": {"code": "...", "message": "...", "details": {}}}
6. Logging configured to capture errors with appropriate log levels
7. Rate limiting implemented to prevent abuse (100 requests/minute per user)

## Tasks / Subtasks

- [ ] Define standard error response schema (AC: 5)
  - [ ] Create `backend/app/schemas/errors.py` module
  - [ ] Define `ErrorDetail` schema with fields: code, message, details (dict)
  - [ ] Define `ErrorResponse` schema with error field of type ErrorDetail
  - [ ] Define error code constants (e.g., VALIDATION_ERROR, NOT_FOUND, UNAUTHORIZED)
  - [ ] Export schemas for use in exception handlers

- [ ] Create custom exception classes
  - [ ] Create `backend/app/utils/exceptions.py` module
  - [ ] Define `BusinessNotFoundException(business_id)` - 404 error
  - [ ] Define `DuplicateResourceException(resource_type, field, value)` - 400 error
  - [ ] Define `UnauthorizedException(message)` - 401 error
  - [ ] Define `ForbiddenException(message)` - 403 error
  - [ ] Define `ValidationException(field, message)` - 422 error
  - [ ] All exceptions inherit from custom base `APIException` class
  - [ ] Each exception includes status_code, error_code, and message attributes

- [ ] Implement custom exception handlers (AC: 1, 2)
  - [ ] Create `backend/app/utils/error_handlers.py` module
  - [ ] Implement handler for custom APIException subclasses
  - [ ] Implement handler for Pydantic ValidationError (422 errors)
  - [ ] Implement handler for SQLAlchemy IntegrityError (database constraint violations)
  - [ ] Implement handler for SQLAlchemy OperationalError (database connection issues)
  - [ ] Implement handler for generic Exception (500 Internal Server Error)
  - [ ] All handlers return ErrorResponse schema
  - [ ] All handlers log errors with appropriate context

- [ ] Handle Pydantic validation errors (AC: 2, 4)
  - [ ] Transform Pydantic ValidationError into user-friendly messages
  - [ ] Include field name and validation issue in error details
  - [ ] Return 422 Unprocessable Entity status code
  - [ ] Format multiple validation errors as array in details field
  - [ ] Test with invalid request payloads (missing fields, wrong types, format violations)

- [ ] Handle database errors (AC: 3)
  - [ ] Catch SQLAlchemy IntegrityError (unique constraint, foreign key violations)
  - [ ] Transform to appropriate HTTP error (400 Bad Request for duplicates)
  - [ ] Include helpful message (e.g., "Business with this website already exists")
  - [ ] Catch OperationalError (connection timeout, server down)
  - [ ] Return 503 Service Unavailable for temporary database issues
  - [ ] Log database errors with full stack trace for debugging

- [ ] Implement request validation middleware
  - [ ] Validate Content-Type header for POST/PUT requests (must be application/json)
  - [ ] Validate request body size limits (max 10MB)
  - [ ] Validate UUID format in path parameters
  - [ ] Return 400 Bad Request for malformed requests
  - [ ] Add validation to all existing endpoints

- [ ] Configure structured logging (AC: 6)
  - [ ] Update `backend/app/config.py` to include logging configuration
  - [ ] Configure Python logging module with JSON formatter for production
  - [ ] Set log levels per environment (DEBUG for dev, INFO for prod)
  - [ ] Log all errors with: timestamp, log_level, request_id, user_id, error details
  - [ ] Create request_id middleware to track requests across logs
  - [ ] Log slow queries (>1 second) at WARNING level
  - [ ] Write logs to stdout (captured by Docker/Kubernetes)

- [ ] Implement rate limiting (AC: 7)
  - [ ] Install slowapi package: add to requirements.txt
  - [ ] Create `backend/app/middleware/rate_limit.py` module
  - [ ] Configure rate limiter using Redis backend (from docker-compose)
  - [ ] Set global limit: 100 requests per minute per user (based on JWT user_id)
  - [ ] Set stricter limits for auth endpoints: 10 requests per minute (prevent brute force)
  - [ ] Return 429 Too Many Requests when limit exceeded
  - [ ] Include Retry-After header in 429 responses
  - [ ] Add rate limit info to response headers (X-RateLimit-Limit, X-RateLimit-Remaining)

- [ ] Add request context middleware
  - [ ] Create `backend/app/middleware/context.py` module
  - [ ] Generate unique request_id (UUID) for each request
  - [ ] Add request_id to response headers (X-Request-ID)
  - [ ] Store request_id in context var for access in logs/handlers
  - [ ] Log incoming requests with method, path, request_id, user_id
  - [ ] Log response with status_code, duration, request_id

- [ ] Register error handlers and middleware in application
  - [ ] Update `backend/app/main.py` to add exception handlers
  - [ ] Register all custom exception handlers with app.add_exception_handler
  - [ ] Add request context middleware
  - [ ] Add rate limiting middleware
  - [ ] Ensure middleware order is correct (context → rate limit → auth → routes)
  - [ ] Test error responses follow standard format

- [ ] Write comprehensive test suite
  - [ ] Create `backend/tests/test_error_handling.py`
  - [ ] Test 404 Not Found responses
  - [ ] Test 400 Bad Request for validation errors
  - [ ] Test 422 Unprocessable Entity for Pydantic validation
  - [ ] Test 401 Unauthorized for missing/invalid tokens
  - [ ] Test 500 Internal Server Error handling
  - [ ] Test 429 Too Many Requests (rate limiting)
  - [ ] Test error response format consistency
  - [ ] Test logging output captures errors correctly
  - [ ] All tests should pass

## Dev Notes

### Learnings from Previous Stories

**From Story 1.5 (Business CRUD - when completed)**
- **Service Layer Errors**: business_service methods should raise custom exceptions (BusinessNotFoundException) instead of returning None
- **Duplicate Detection**: Use DuplicateResourceException when website_url already exists
- **Validation**: Pydantic schemas handle basic validation, but custom business logic validation needs exception handling

**From Story 1.4 (JWT Authentication - when completed)**
- **Auth Errors**: get_current_user dependency should raise UnauthorizedException for invalid tokens
- **Token Validation**: Clear error messages help frontend handle expired tokens differently from invalid tokens

**From Story 1.3 (Status: review)**
- **Current Error Handling**: Basic error handling exists, but not comprehensive
- **Logging Setup**: Settings.configure_logging() method already exists in config.py
- **Redis Available**: Redis service configured in docker-compose for rate limiting backend

[Source: stories/1-3-fastapi-application-foundation.md#Dev-Agent-Record]

### Project Structure

```
backend/app/
├── middleware/
│   ├── __init__.py      # NEW: Create middleware package
│   ├── context.py       # NEW: Request context and ID tracking
│   └── rate_limit.py    # NEW: Rate limiting configuration
├── schemas/
│   ├── errors.py        # NEW: Error response schemas
│   └── __init__.py
├── utils/
│   ├── exceptions.py    # NEW: Custom exception classes
│   ├── error_handlers.py # NEW: Exception handlers
│   └── __init__.py
└── main.py              # UPDATE: Register handlers and middleware
```

### Technical Constraints

- **Rate Limiting**: slowapi (FastAPI wrapper for flask-limiter)
- **Redis**: Required for distributed rate limiting (already in docker-compose)
- **Logging**: Python logging module with JSON formatter (python-json-logger)
- **Request ID**: Use UUID4 for unique request identification
- **Log Retention**: Stdout logs captured by container orchestration platform

### Error Response Format

**Standard Error Response:**
```json
{
  "error": {
    "code": "BUSINESS_NOT_FOUND",
    "message": "Business with ID 123e4567-e89b-12d3-a456-426614174000 not found",
    "details": {
      "business_id": "123e4567-e89b-12d3-a456-426614174000",
      "timestamp": "2025-11-01T12:00:00Z",
      "request_id": "abc-123-def-456"
    }
  }
}
```

**Validation Error Response:**
```json
{
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
      "request_id": "abc-123-def-456"
    }
  }
}
```

### Error Code Standards

**Error Codes:**
- `VALIDATION_ERROR` - Pydantic validation failure (422)
- `NOT_FOUND` - Resource not found (404)
- `BUSINESS_NOT_FOUND` - Specific business not found (404)
- `USER_NOT_FOUND` - User not found (404)
- `DUPLICATE_RESOURCE` - Resource already exists (400)
- `UNAUTHORIZED` - Authentication required or failed (401)
- `FORBIDDEN` - Insufficient permissions (403)
- `RATE_LIMIT_EXCEEDED` - Too many requests (429)
- `DATABASE_ERROR` - Database operation failed (500)
- `INTERNAL_ERROR` - Unexpected server error (500)

### Rate Limiting Strategy

**Rate Limits by Endpoint Type:**
- **Auth Endpoints** (/api/auth/*): 10 requests/minute per IP (prevent brute force)
- **Read Endpoints** (GET): 100 requests/minute per user
- **Write Endpoints** (POST/PUT/DELETE): 50 requests/minute per user
- **Public Endpoints** (health check): No limit

**Rate Limit Headers:**
- `X-RateLimit-Limit`: Maximum requests allowed in window
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Unix timestamp when limit resets
- `Retry-After`: Seconds to wait before retrying (on 429 response)

### Logging Best Practices

**What to Log:**
- All errors (ERROR level) with stack traces
- Authentication failures (WARNING level)
- Slow queries >1s (WARNING level)
- All requests with duration (INFO level)
- Rate limit exceeded (WARNING level)
- Database connection issues (ERROR level)

**What NOT to Log:**
- Passwords or tokens (security risk)
- Full request bodies with sensitive data
- PII without anonymization (GDPR compliance)

**Log Format (JSON):**
```json
{
  "timestamp": "2025-11-01T12:00:00Z",
  "level": "ERROR",
  "request_id": "abc-123",
  "user_id": "user-uuid",
  "endpoint": "POST /api/businesses",
  "error_code": "DUPLICATE_RESOURCE",
  "message": "Business with this website already exists",
  "stack_trace": "..."
}
```

### Middleware Execution Order

**Correct Order (outer to inner):**
1. **Request Context Middleware** - Generate request_id, start logging
2. **Rate Limiting Middleware** - Check rate limits
3. **CORS Middleware** - Handle CORS headers (already configured)
4. **Authentication Middleware** - Validate JWT (via dependencies)
5. **Route Handler** - Execute business logic
6. **Exception Handlers** - Catch and format errors
7. **Response** - Return to client

### References

- [Source: docs/epics.md#Story-1.6]
- [Source: docs/PRD.md#NFR005] (Security and input validation)
- FastAPI Error Handling: https://fastapi.tiangolo.com/tutorial/handling-errors/
- slowapi: https://github.com/laurents/slowapi
- Python Logging: https://docs.python.org/3/library/logging.html

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

- 2025-11-01: Story created from Epic 1, Story 6 in epics.md
