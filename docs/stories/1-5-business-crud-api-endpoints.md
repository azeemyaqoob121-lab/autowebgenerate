# Story 1.5: Business CRUD API Endpoints

Status: todo

## Story

As a backend developer,
I want to create CRUD endpoints for business management,
So that frontend can interact with business data.

## Acceptance Criteria

1. GET /api/businesses endpoint created with pagination (limit, offset)
2. GET /api/businesses/{id} endpoint created returning single business details
3. POST /api/businesses endpoint created (protected, for manual business entry)
4. PUT /api/businesses/{id} endpoint created for updates
5. DELETE /api/businesses/{id} endpoint created (soft delete preferred)
6. Query filtering supported: score range, location, category
7. Pydantic schemas created for request/response validation
8. All endpoints return proper HTTP status codes and error messages
9. Endpoints tested with sample data

## Tasks / Subtasks

- [ ] Create Pydantic schemas for Business (AC: 7)
  - [ ] Create `backend/app/schemas/business.py` module
  - [ ] Define `BusinessBase` schema with common fields: name, email, phone, address, website_url, category, description, location
  - [ ] Define `BusinessCreate` schema (inherits BusinessBase) for POST requests
  - [ ] Define `BusinessUpdate` schema (all fields optional) for PUT requests
  - [ ] Define `BusinessResponse` schema (includes id, score, created_at, updated_at, evaluation status, template status)
  - [ ] Define `BusinessListResponse` schema for paginated list: items (List[BusinessResponse]), total, limit, offset
  - [ ] Add field validators (email format, URL format, phone format)

- [ ] Create business CRUD service layer
  - [ ] Create `backend/app/services/business_service.py` module
  - [ ] Implement `get_businesses(db, skip, limit, filters)` - returns paginated list
  - [ ] Implement `get_business_by_id(db, business_id)` - returns single business or None
  - [ ] Implement `get_business_by_website(db, website_url)` - check for duplicates
  - [ ] Implement `create_business(db, business_data)` - creates and returns new business
  - [ ] Implement `update_business(db, business_id, business_data)` - updates and returns business
  - [ ] Implement `delete_business(db, business_id)` - soft delete (set deleted_at field)
  - [ ] Implement filtering logic for score_min, score_max, location, category

- [ ] Add soft delete support to Business model
  - [ ] Update `backend/app/models/business.py` to add `deleted_at` field (DateTime, nullable)
  - [ ] Create Alembic migration: `alembic revision --autogenerate -m "add_soft_delete_to_business"`
  - [ ] Apply migration: `alembic upgrade head`
  - [ ] Update queries to exclude deleted records by default (WHERE deleted_at IS NULL)

- [ ] Implement GET /api/businesses endpoint (AC: 1, 6)
  - [ ] Create `backend/app/routes/businesses.py` router
  - [ ] Implement list endpoint with query parameters: limit (default 50, max 100), offset (default 0)
  - [ ] Add filtering parameters: score_min, score_max, location, category, search (text search)
  - [ ] Use business_service.get_businesses with filters
  - [ ] Return BusinessListResponse with total count
  - [ ] Add sorting support (sort_by, sort_order query params)
  - [ ] Protect endpoint with get_current_user dependency

- [ ] Implement GET /api/businesses/{id} endpoint (AC: 2)
  - [ ] Add route handler accepting business_id (UUID) path parameter
  - [ ] Use business_service.get_business_by_id
  - [ ] Return BusinessResponse if found
  - [ ] Return 404 Not Found if business doesn't exist
  - [ ] Include related data: latest evaluation scores, template count
  - [ ] Protect endpoint with get_current_user dependency

- [ ] Implement POST /api/businesses endpoint (AC: 3)
  - [ ] Add route handler accepting BusinessCreate schema in request body
  - [ ] Validate website_url is unique using business_service.get_business_by_website
  - [ ] Return 400 Bad Request if website already exists
  - [ ] Use business_service.create_business to insert record
  - [ ] Return 201 Created with BusinessResponse
  - [ ] Protect endpoint with get_current_user dependency

- [ ] Implement PUT /api/businesses/{id} endpoint (AC: 4)
  - [ ] Add route handler accepting business_id and BusinessUpdate schema
  - [ ] Check business exists, return 404 if not found
  - [ ] If website_url changed, validate uniqueness
  - [ ] Use business_service.update_business to update record
  - [ ] Return 200 OK with updated BusinessResponse
  - [ ] Protect endpoint with get_current_user dependency

- [ ] Implement DELETE /api/businesses/{id} endpoint (AC: 5)
  - [ ] Add route handler accepting business_id path parameter
  - [ ] Check business exists, return 404 if not found
  - [ ] Use business_service.delete_business (soft delete: set deleted_at)
  - [ ] Return 204 No Content on success
  - [ ] Protect endpoint with get_current_user dependency
  - [ ] Optional: Add hard delete query parameter for permanent deletion

- [ ] Implement text search functionality
  - [ ] Add search query parameter to GET /api/businesses
  - [ ] Search across: name, category, location, description fields
  - [ ] Use PostgreSQL ILIKE for case-insensitive search
  - [ ] Support multiple search terms (split by spaces, AND logic)
  - [ ] Test search returns relevant results

- [ ] Register businesses router in main application
  - [ ] Import businesses router in `backend/app/main.py`
  - [ ] Include router: `app.include_router(businesses.router, prefix="/api/businesses", tags=["businesses"])`
  - [ ] Verify endpoints appear in /docs Swagger UI
  - [ ] Test all endpoints manually

- [ ] Write comprehensive test suite (AC: 9)
  - [ ] Create `backend/tests/test_businesses.py`
  - [ ] Test GET /api/businesses (pagination, filtering, sorting)
  - [ ] Test GET /api/businesses/{id} (found, not found)
  - [ ] Test POST /api/businesses (success, duplicate website, validation errors)
  - [ ] Test PUT /api/businesses/{id} (success, not found, validation)
  - [ ] Test DELETE /api/businesses/{id} (success, not found)
  - [ ] Test authentication required (401 without token)
  - [ ] Test text search functionality
  - [ ] All tests should pass with sample data

## Dev Notes

### Learnings from Previous Stories

**From Story 1.4 (JWT Authentication - when completed)**
- **Protected Routes**: Use `get_current_user` dependency from `backend/app/utils/security.py` to protect endpoints
- **Authentication Testing**: Include valid JWT token in test requests (Authorization: Bearer {token})
- **User Context**: Current user available in route handlers via dependency injection

**From Story 1.3 (Status: review)**
- **Database Sessions**: Use `get_db()` dependency in all route handlers
- **Test Client**: Use `client` fixture from conftest.py for integration tests
- **Error Responses**: Follow consistent format: {"error": {"code": "...", "message": "...", "details": {}}}

**From Story 1.2 (Status: review)**
- **Business Model**: Already defined in `backend/app/models/business.py` with all required fields
- **Relationships**: Business has relationships to Evaluation and Template models
- **Indexes**: Already indexed on score, location, category for efficient filtering

[Source: stories/1-2-postgresql-database-schema-and-models.md#Dev-Agent-Record]

### Project Structure

```
backend/app/
├── models/
│   ├── business.py      # UPDATE: Add deleted_at field
│   └── __init__.py
├── routes/
│   ├── businesses.py    # NEW: Business CRUD endpoints
│   └── __init__.py
├── schemas/
│   ├── business.py      # NEW: Business request/response schemas
│   └── __init__.py
├── services/
│   ├── business_service.py  # NEW: Business logic layer
│   └── __init__.py
└── main.py              # UPDATE: Include businesses router
```

### Technical Constraints

- **Pagination**: Default limit 50, maximum limit 100 to prevent excessive data transfer
- **UUID Format**: All IDs are UUIDs, validate format in path parameters
- **Soft Delete**: Prefer soft delete (deleted_at timestamp) to preserve referential integrity
- **Filtering**: Support multiple filters with AND logic
- **Response Times**: List queries should return in <500ms per NFR001

### API Design Decisions

**Why Service Layer:**
- Separates business logic from HTTP concerns
- Makes logic reusable across different routes
- Easier to test business logic independently
- Follows clean architecture principles

**Why Soft Delete:**
- Preserves historical data (evaluations, templates linked to business)
- Enables "undo" functionality
- Supports audit trails
- Can add hard delete for admin users if needed

**Why Pagination:**
- Prevents large result sets from overwhelming clients
- Improves response times
- Reduces memory usage on backend
- Standard REST API pattern

**Why Protected Endpoints:**
- Prevents unauthorized access to business data
- Tracks which user created/modified records
- Enables future audit logging
- Per PRD security requirements

### Query Optimization

**Filtering Strategy:**
- Use SQLAlchemy filters for database-level filtering (most efficient)
- Add indexes on commonly filtered fields (score, location, category - already done in Story 1.2)
- Use LIMIT/OFFSET for pagination
- Count total matching records separately for pagination metadata

**Search Implementation:**
- Use PostgreSQL ILIKE for case-insensitive text search
- Search across multiple fields with OR logic
- Consider full-text search (to_tsvector) for future enhancement if performance needed
- Limit search term length to prevent abuse

### Response Schemas

**BusinessResponse includes:**
- All business data fields
- Computed fields: has_evaluation, has_templates, template_generation_status
- Relationships: evaluation_count, template_count
- Timestamps: created_at, updated_at, deleted_at (if soft deleted)

**BusinessListResponse includes:**
- items: Array of BusinessResponse
- total: Total count of matching records (before pagination)
- limit: Current page size
- offset: Current offset
- page: Computed page number (offset / limit + 1)
- pages: Total pages (total / limit, rounded up)

### Error Handling

**Common HTTP Status Codes:**
- 200 OK: Successful GET/PUT
- 201 Created: Successful POST
- 204 No Content: Successful DELETE
- 400 Bad Request: Validation errors, duplicate data
- 401 Unauthorized: Missing or invalid authentication token
- 404 Not Found: Business ID doesn't exist
- 422 Unprocessable Entity: Pydantic validation errors
- 500 Internal Server Error: Unexpected errors (should be logged)

### References

- [Source: docs/epics.md#Story-1.5]
- [Source: docs/PRD.md#FR006] (Persistent storage requirement)
- [Source: docs/PRD.md#FR018-FR020] (API requirements)
- FastAPI CRUD: https://fastapi.tiangolo.com/tutorial/sql-databases/#crud-utils
- SQLAlchemy Filtering: https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html

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

- 2025-11-01: Story created from Epic 1, Story 5 in epics.md
