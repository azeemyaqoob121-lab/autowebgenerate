"""Business schemas for request/response validation"""
from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class BusinessBase(BaseModel):
    """Base business schema with common fields"""
    name: str = Field(..., min_length=1, max_length=255, description="Business name")
    email: Optional[str] = Field(None, max_length=255, description="Business email address")
    phone: Optional[str] = Field(None, max_length=50, description="Business phone number")
    address: Optional[str] = Field(None, max_length=500, description="Business physical address")
    website_url: HttpUrl = Field(..., description="Business website URL (must be unique)")
    category: Optional[str] = Field(None, max_length=100, description="Business category/industry")
    description: Optional[str] = Field(None, description="Business description")
    location: Optional[str] = Field(None, max_length=255, description="Business location/city")


class BusinessCreate(BusinessBase):
    """Schema for creating a new business"""
    pass

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Acme Plumbing Ltd",
                "email": "contact@acmeplumbing.co.uk",
                "phone": "+44 20 1234 5678",
                "address": "123 High Street, London",
                "website_url": "https://acmeplumbing.co.uk",
                "category": "Plumbing",
                "description": "Professional plumbing services in London",
                "location": "London"
            }
        }


class BusinessUpdate(BaseModel):
    """Schema for updating a business (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = Field(None, max_length=500)
    website_url: Optional[HttpUrl] = None
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=255)
    score: Optional[int] = Field(None, ge=0, le=100, description="Evaluation score")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Acme Plumbing Ltd",
                "phone": "+44 20 9999 8888",
                "score": 85
            }
        }


class BusinessResponse(BusinessBase):
    """Schema for business response"""
    id: UUID
    score: Optional[int] = Field(None, description="Aggregate evaluation score")
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    # Additional computed fields
    has_evaluation: bool = Field(default=False, description="Whether business has been evaluated")
    has_template: bool = Field(default=False, description="Whether business has generated templates")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Acme Plumbing Ltd",
                "email": "contact@acmeplumbing.co.uk",
                "phone": "+44 20 1234 5678",
                "address": "123 High Street, London",
                "website_url": "https://acmeplumbing.co.uk",
                "category": "Plumbing",
                "description": "Professional plumbing services in London",
                "location": "London",
                "score": 75,
                "created_at": "2025-11-01T12:00:00Z",
                "updated_at": "2025-11-01T12:00:00Z",
                "deleted_at": None,
                "has_evaluation": True,
                "has_template": False
            }
        }


class BusinessListResponse(BaseModel):
    """Schema for paginated business list response"""
    items: List[BusinessResponse] = Field(..., description="List of businesses")
    total: int = Field(..., description="Total number of businesses matching filters")
    limit: int = Field(..., description="Number of items per page")
    offset: int = Field(..., description="Offset from start")
    has_next: bool = Field(..., description="Whether there are more items")
    has_prev: bool = Field(..., description="Whether there are previous items")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "Acme Plumbing Ltd",
                        "website_url": "https://acmeplumbing.co.uk",
                        "location": "London",
                        "score": 75,
                        "created_at": "2025-11-01T12:00:00Z",
                        "updated_at": "2025-11-01T12:00:00Z"
                    }
                ],
                "total": 150,
                "limit": 50,
                "offset": 0,
                "has_next": True,
                "has_prev": False
            }
        }


class BusinessFilters(BaseModel):
    """Schema for business filtering parameters"""
    score_min: Optional[int] = Field(None, ge=0, le=100, description="Minimum score filter")
    score_max: Optional[int] = Field(None, ge=0, le=100, description="Maximum score filter")
    location: Optional[str] = Field(None, description="Filter by location")
    category: Optional[str] = Field(None, description="Filter by category")
    search: Optional[str] = Field(None, description="Text search across name, description, category")
    limit: int = Field(50, ge=1, le=100, description="Number of items per page")
    offset: int = Field(0, ge=0, description="Offset from start")
    sort_by: Optional[str] = Field("created_at", description="Field to sort by")
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$", description="Sort order")

    @field_validator('score_max')
    @classmethod
    def validate_score_range(cls, v, info):
        """Ensure score_max >= score_min if both provided"""
        if v is not None and 'score_min' in info.data and info.data['score_min'] is not None:
            if v < info.data['score_min']:
                raise ValueError('score_max must be greater than or equal to score_min')
        return v


class BusinessDiscoveryRequest(BaseModel):
    """Schema for discovering real businesses via Google Places API"""
    location: str = Field(..., min_length=1, max_length=255, description="UK location (e.g., 'London', 'Manchester')")
    category: str = Field(..., min_length=1, max_length=100, description="Business category/niche (e.g., 'plumber', 'restaurant')")
    max_results: int = Field(10, ge=1, le=20, description="Maximum number of businesses to discover")
    auto_evaluate: bool = Field(True, description="Automatically evaluate discovered businesses")

    class Config:
        json_schema_extra = {
            "example": {
                "location": "London",
                "category": "plumber",
                "max_results": 10,
                "auto_evaluate": True
            }
        }


class BusinessDiscoveryResponse(BaseModel):
    """Schema for business discovery response"""
    discovered: int = Field(..., description="Number of businesses discovered")
    saved: int = Field(..., description="Number of businesses saved to database")
    evaluated: int = Field(..., description="Number of businesses evaluated")
    templates_generated: int = Field(..., description="Number of templates generated for low-scoring businesses")
    businesses: List[BusinessResponse] = Field(..., description="List of discovered businesses")

    class Config:
        json_schema_extra = {
            "example": {
                "discovered": 10,
                "saved": 8,
                "evaluated": 7,
                "templates_generated": 3,
                "businesses": []
            }
        }
