"""Evaluation schemas for request/response validation"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime


class EvaluationCreate(BaseModel):
    """Schema for creating/triggering a new evaluation"""
    business_id: UUID = Field(..., description="Business ID to evaluate")

    class Config:
        json_schema_extra = {
            "example": {
                "business_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }


class EvaluationResponse(BaseModel):
    """Schema for evaluation response"""
    id: UUID
    business_id: UUID
    performance_score: float = Field(..., ge=0, le=1, description="Performance score (0-1)")
    seo_score: float = Field(..., ge=0, le=1, description="SEO score (0-1)")
    accessibility_score: float = Field(..., ge=0, le=1, description="Accessibility score (0-1)")
    aggregate_score: float = Field(..., ge=0, le=100, description="Aggregate score (0-100)")
    lighthouse_data: Optional[Dict[str, Any]] = Field(None, description="Full Lighthouse report data")
    evaluated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "business_id": "123e4567-e89b-12d3-a456-426614174000",
                "performance_score": 0.75,
                "seo_score": 0.82,
                "accessibility_score": 0.68,
                "aggregate_score": 65,
                "lighthouse_data": {
                    "performance": 75,
                    "seo": 82,
                    "accessibility": 68
                },
                "evaluated_at": "2025-11-03T12:00:00Z"
            }
        }
