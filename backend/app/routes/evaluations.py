"""Evaluation API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.models import User
from app.schemas.evaluation import EvaluationCreate, EvaluationResponse
from app.services import evaluation_service
from app.utils.security import get_current_user


router = APIRouter()


@router.get(
    "/businesses/{business_id}/evaluations",
    response_model=EvaluationResponse,
    summary="Get business evaluation",
    description="Get the latest evaluation for a specific business"
)
async def get_business_evaluation(
    business_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the latest evaluation for a business.

    Requires authentication.

    Returns:
    - Latest evaluation with all scores and Lighthouse data
    - 404 if business has no evaluation yet
    """
    evaluation = evaluation_service.get_evaluation_by_business_id(db, business_id)

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No evaluation found for business {business_id}"
        )

    return evaluation


@router.get(
    "/businesses/{business_id}/evaluation",
    response_model=EvaluationResponse,
    summary="Get business evaluation (alias)",
    description="Get the latest evaluation for a specific business (singular alias)"
)
async def get_business_evaluation_singular(
    business_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the latest evaluation for a business (singular alias).

    This is an alias for /businesses/{business_id}/evaluations to support both singular and plural forms.

    Requires authentication.

    Returns:
    - Latest evaluation with all scores and Lighthouse data
    - 404 if business has no evaluation yet
    """
    return await get_business_evaluation(business_id, current_user, db)


@router.post(
    "/evaluations",
    response_model=EvaluationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create/Trigger evaluation",
    description="Create a new website evaluation for a business"
)
async def create_evaluation(
    evaluation_data: EvaluationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger a new website evaluation for a business.

    Requires authentication.

    This endpoint will:
    1. Evaluate the website using Lighthouse (currently mock data)
    2. Generate performance, SEO, and accessibility scores
    3. Calculate aggregate quality score
    4. Update business.score field
    5. Return full evaluation data

    Returns:
    - 201 Created with evaluation details
    - 404 if business not found
    - 400 if evaluation fails
    """
    try:
        evaluation = evaluation_service.create_evaluation(db, evaluation_data.business_id)
        return evaluation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create evaluation: {str(e)}"
        )
