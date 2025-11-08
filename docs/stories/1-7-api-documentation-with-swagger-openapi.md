# Story 1.7: API Documentation with Swagger/OpenAPI

Status: todo

## Story

As a frontend developer,
I want auto-generated API documentation,
So that I can understand available endpoints and their schemas.

## Acceptance Criteria

1. FastAPI automatic OpenAPI schema generation enabled
2. Swagger UI accessible at /docs endpoint
3. ReDoc documentation accessible at /redoc endpoint
4. All endpoints documented with descriptions and example requests/responses
5. Pydantic schemas provide clear field descriptions and types
6. Authentication requirements clearly indicated in documentation
7. Example values provided for all request bodies

## Tasks / Subtasks

- [ ] Configure OpenAPI metadata (AC: 1)
  - [ ] Update `backend/app/main.py` create_app() to set OpenAPI metadata
  - [ ] Set API title: "AutoWeb Outreach AI API"
  - [ ] Set API version from settings.API_VERSION
  - [ ] Set API description with project overview and key features
  - [ ] Add contact information (name, email, URL)
  - [ ] Add license information (if applicable)
  - [ ] Configure OpenAPI tags for endpoint grouping

- [ ] Enhance Swagger UI configuration (AC: 2)
  - [ ] Verify /docs endpoint is accessible (enabled by default)
  - [ ] Configure Swagger UI settings (deepLinking, displayRequestDuration)
  - [ ] Add custom CSS for branding (optional enhancement)
  - [ ] Enable "Try it out" functionality for all endpoints
  - [ ] Test Swagger UI renders correctly with all routes

- [ ] Enable ReDoc documentation (AC: 3)
  - [ ] Verify /redoc endpoint is accessible (enabled by default)
  - [ ] ReDoc provides alternative documentation view
  - [ ] Test ReDoc renders correctly with all routes
  - [ ] ReDoc automatically includes all OpenAPI spec info

- [ ] Document authentication in OpenAPI spec (AC: 6)
  - [ ] Configure OpenAPI security scheme for JWT Bearer tokens
  - [ ] Define security scheme: type="http", scheme="bearer", bearerFormat="JWT"
  - [ ] Mark protected endpoints with security requirement
  - [ ] Swagger UI shows "Authorize" button for entering tokens
  - [ ] Test authentication flow in Swagger UI (login → get token → authorize → call protected endpoint)

- [ ] Add endpoint descriptions and summaries (AC: 4)
  - [ ] Add docstrings to all route handlers (FastAPI auto-extracts these)
  - [ ] Provide summary (short description) for each endpoint
  - [ ] Provide detailed description explaining purpose and behavior
  - [ ] Document query parameters with descriptions
  - [ ] Document path parameters with descriptions
  - [ ] Document request body fields
  - [ ] Document response codes and their meanings

- [ ] Enhance Pydantic schemas with descriptions (AC: 5)
  - [ ] Add Field(..., description="...") to all schema fields
  - [ ] Provide clear, user-friendly field descriptions
  - [ ] Specify field types explicitly (str, int, EmailStr, UUID, etc.)
  - [ ] Mark optional vs required fields clearly
  - [ ] Add field constraints (min_length, max_length, ge, le)
  - [ ] Review all schemas: Business, Auth, Error schemas

- [ ] Add example values to schemas (AC: 7)
  - [ ] Add Field(..., example="...") to schema fields
  - [ ] Provide realistic example values (not "string" or "user@example.com")
  - [ ] Add Config class with schema_extra for complex examples
  - [ ] Examples should demonstrate actual usage patterns
  - [ ] Test examples appear in Swagger UI request bodies

- [ ] Document error responses
  - [ ] Document possible error codes for each endpoint
  - [ ] Add responses parameter to route decorators
  - [ ] Include 400, 401, 404, 422, 500 responses where applicable
  - [ ] Reference ErrorResponse schema in error responses
  - [ ] Provide example error payloads

- [ ] Add API usage examples
  - [ ] Create example request/response pairs for common workflows
  - [ ] Document authentication flow (register → login → get token)
  - [ ] Document business CRUD workflow (create → read → update → delete)
  - [ ] Add examples to endpoint descriptions
  - [ ] Consider adding separate API usage guide (markdown doc)

- [ ] Organize endpoints with tags
  - [ ] Group auth endpoints under "Authentication" tag
  - [ ] Group business endpoints under "Businesses" tag
  - [ ] Future: Scraping, Evaluations, Templates tags
  - [ ] Tags appear as collapsible sections in Swagger UI
  - [ ] Add tag descriptions in OpenAPI metadata

- [ ] Test documentation completeness
  - [ ] Verify all endpoints appear in /docs
  - [ ] Check all endpoints have descriptions
  - [ ] Verify authentication scheme works in Swagger UI
  - [ ] Test "Try it out" for each endpoint type (GET, POST, PUT, DELETE)
  - [ ] Verify error responses documented
  - [ ] Check ReDoc alternative view

- [ ] Create API documentation README
  - [ ] Create `docs/api-documentation.md` file
  - [ ] Document how to access API docs (/docs, /redoc)
  - [ ] Explain authentication process for Swagger UI
  - [ ] Provide curl examples for common operations
  - [ ] Link to OpenAPI JSON spec (/openapi.json)
  - [ ] Document rate limits and error codes

## Dev Notes

### Learnings from Previous Stories

**From Story 1.6 (Error Handling - when completed)**
- **Error Schemas**: ErrorResponse schema should be referenced in endpoint documentation
- **Error Codes**: Document standard error codes (VALIDATION_ERROR, NOT_FOUND, etc.)
- **Rate Limiting**: Document rate limits in endpoint descriptions

**From Story 1.5 (Business CRUD - when completed)**
- **Business Schemas**: BusinessCreate, BusinessUpdate, BusinessResponse schemas need field descriptions
- **Pagination**: Document pagination parameters (limit, offset) clearly
- **Filtering**: Document filter parameters (score_min, score_max, location, category)

**From Story 1.4 (JWT Authentication - when completed)**
- **Auth Flow**: Document complete authentication workflow
- **Token Format**: Explain JWT token structure and expiration
- **Protected Routes**: Clearly mark which endpoints require authentication

**From Story 1.3 (Status: review)**
- **Health Check**: Document health check response format
- **CORS**: May need to document CORS configuration for frontend developers

[Source: stories/1-3-fastapi-application-foundation.md#Dev-Agent-Record]

### Project Structure

```
backend/app/
├── main.py              # UPDATE: OpenAPI metadata and security scheme
├── routes/
│   ├── auth.py          # UPDATE: Add docstrings and examples
│   └── businesses.py    # UPDATE: Add docstrings and examples
├── schemas/
│   ├── auth.py          # UPDATE: Add Field descriptions and examples
│   ├── business.py      # UPDATE: Add Field descriptions and examples
│   └── errors.py        # UPDATE: Add Field descriptions
└── ...

docs/
└── api-documentation.md # NEW: API usage guide
```

### Technical Constraints

- **FastAPI Version**: 0.109.0+ (automatic OpenAPI 3.1.0 generation)
- **Documentation URLs**: /docs (Swagger UI), /redoc (ReDoc), /openapi.json (OpenAPI spec)
- **Schema Format**: OpenAPI 3.1.0 (latest standard)
- **Authentication**: JWT Bearer token scheme

### OpenAPI Metadata Configuration

**API Information:**
```python
app = FastAPI(
    title="AutoWeb Outreach AI API",
    description="""
    AutoWeb Outreach AI automates lead generation for web development agencies.

    ## Features
    * **Business Discovery**: Scrape UK business directories
    * **Website Evaluation**: Lighthouse scoring and analysis
    * **AI Template Generation**: GPT-4 powered website previews
    * **Lead Management**: CRUD operations for business data

    ## Authentication
    All endpoints require JWT Bearer token authentication except /auth endpoints.
    """,
    version=settings.API_VERSION,
    contact={
        "name": "AutoWeb Outreach AI",
        "email": "support@autoweb.ai",
    },
    license_info={
        "name": "Proprietary",
    },
)
```

**Security Scheme:**
```python
from fastapi.security import HTTPBearer

security_scheme = HTTPBearer()

# In OpenAPI spec:
{
    "securitySchemes": {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
}
```

### Pydantic Schema Documentation Patterns

**Field Descriptions:**
```python
class BusinessCreate(BaseModel):
    name: str = Field(
        ...,
        description="Business name as it appears publicly",
        example="ABC Plumbing Services Ltd"
    )
    email: EmailStr = Field(
        ...,
        description="Primary contact email address",
        example="contact@abcplumbing.co.uk"
    )
    website_url: HttpUrl = Field(
        ...,
        description="Business website URL (must be valid and accessible)",
        example="https://www.abcplumbing.co.uk"
    )
```

**Schema Examples:**
```python
class BusinessCreate(BaseModel):
    # ... field definitions ...

    class Config:
        schema_extra = {
            "example": {
                "name": "ABC Plumbing Services Ltd",
                "email": "contact@abcplumbing.co.uk",
                "phone": "+44 20 1234 5678",
                "address": "123 High Street, Manchester, M1 1AA",
                "website_url": "https://www.abcplumbing.co.uk",
                "category": "Plumbing & Heating",
                "description": "Professional plumbing and heating services in Greater Manchester",
                "location": "Manchester"
            }
        }
```

### Endpoint Documentation Patterns

**Route Handler Docstrings:**
```python
@router.post("/", response_model=BusinessResponse, status_code=201)
async def create_business(
    business: BusinessCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new business record.

    Creates a new business in the database with the provided information.
    The website URL must be unique - duplicate URLs will return an error.

    - **name**: Business name (required)
    - **email**: Contact email (required, must be valid email format)
    - **website_url**: Business website (required, must be unique and valid URL)
    - **category**: Business category/industry (required)
    - **location**: Geographic location (city or postcode)

    Returns the created business with generated ID and timestamps.

    **Authentication Required**: Yes (JWT Bearer token)
    """
    # Implementation...
```

**Response Documentation:**
```python
@router.get(
    "/{business_id}",
    response_model=BusinessResponse,
    responses={
        200: {"description": "Business found and returned"},
        401: {"description": "Authentication required", "model": ErrorResponse},
        404: {"description": "Business not found", "model": ErrorResponse},
    }
)
```

### OpenAPI Tags

**Tag Definitions:**
```python
tags_metadata = [
    {
        "name": "authentication",
        "description": "User registration, login, and token management"
    },
    {
        "name": "businesses",
        "description": "Business CRUD operations and search"
    },
    {
        "name": "health",
        "description": "System health and status checks"
    },
]

app = FastAPI(..., openapi_tags=tags_metadata)
```

**Using Tags in Routes:**
```python
router = APIRouter(prefix="/api/businesses", tags=["businesses"])
```

### Documentation Testing Checklist

**Swagger UI (/docs):**
- [ ] All endpoints visible and grouped by tags
- [ ] "Authorize" button allows JWT token entry
- [ ] Request body examples are realistic and helpful
- [ ] Response schemas show correct structure
- [ ] "Try it out" works for all endpoint types
- [ ] Error responses documented

**ReDoc (/redoc):**
- [ ] Alternative documentation view renders correctly
- [ ] All content from Swagger UI present
- [ ] Better for reading (less interactive)

**OpenAPI JSON (/openapi.json):**
- [ ] Valid OpenAPI 3.1.0 spec
- [ ] Can be imported into Postman or other tools
- [ ] Contains all metadata, schemas, paths

### References

- [Source: docs/epics.md#Story-1.7]
- [Source: docs/PRD.md#FR018] (RESTful API requirement)
- FastAPI OpenAPI: https://fastapi.tiangolo.com/tutorial/metadata/
- FastAPI Security Documentation: https://fastapi.tiangolo.com/tutorial/security/
- OpenAPI 3.1.0 Spec: https://swagger.io/specification/
- Pydantic Schema Documentation: https://docs.pydantic.dev/latest/usage/schema/

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

- 2025-11-01: Story created from Epic 1, Story 7 in epics.md
