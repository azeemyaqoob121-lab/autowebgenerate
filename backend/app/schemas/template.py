"""Template schemas for request/response validation"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from datetime import datetime


class ImprovementItem(BaseModel):
    """Single improvement item"""
    category: str = Field(..., description="Category: performance, seo, accessibility, mobile")
    description: str = Field(..., description="What was improved")
    impact: str = Field(..., description="Impact level: high, medium, low")


class TemplateResponse(BaseModel):
    """Schema for template response"""
    id: UUID
    business_id: UUID
    html_content: str
    css_content: str
    js_content: Optional[str] = None
    improvements_made: Union[Dict[str, Any], List[ImprovementItem], List[Dict[str, Any]]] = {}  # Support both old (list) and new (dict) formats
    media_assets: Optional[Dict[str, Any]] = None  # Added for premium templates
    variant_number: int
    generated_at: datetime

    @field_validator('improvements_made', mode='before')
    @classmethod
    def normalize_improvements(cls, v):
        """Normalize improvements_made to always return a dict for consistency"""
        if v is None:
            return {}
        if isinstance(v, dict):
            return v
        if isinstance(v, list):
            # Convert list to dict format for consistency
            result = {}
            for item in v:
                if isinstance(item, dict):
                    category = item.get('category', 'general')
                    if category not in result:
                        result[category] = []
                    result[category].append(item.get('description', ''))
            return result if result else {}
        return {}

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "business_id": "123e4567-e89b-12d3-a456-426614174001",
                "html_content": "<!DOCTYPE html>...",
                "css_content": "body { ... }",
                "js_content": None,
                "improvements_made": {
                    "performance": ["Optimized images", "Lazy loading"],
                    "seo": ["Meta tags", "Schema.org"],
                    "accessibility": ["ARIA labels", "Semantic HTML"],
                    "design": ["Responsive layout", "Modern UI"]
                },
                "media_assets": {
                    "images": [],
                    "hero_video": None,
                    "business_type": "restaurant"
                },
                "variant_number": 1,
                "generated_at": "2025-11-01T12:00:00Z"
            }
        }


class TemplateListResponse(BaseModel):
    """Schema for list of templates"""
    templates: List[TemplateResponse]
    total: int

    class Config:
        json_schema_extra = {
            "example": {
                "templates": [],
                "total": 3
            }
        }


class TemplateGenerateRequest(BaseModel):
    """Schema for template generation request"""
    num_variants: int = Field(default=3, ge=1, le=3, description="Number of variants to generate (1-3)")

    class Config:
        json_schema_extra = {
            "example": {
                "num_variants": 3
            }
        }
