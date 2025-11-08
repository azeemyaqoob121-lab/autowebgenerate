"""Template API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import uuid
import logging

from app.database import get_db
from app.models import Business, Template, User
from app.schemas.template import (
    TemplateResponse,
    TemplateListResponse,
    TemplateGenerateRequest
)
from app.utils.security import get_current_user
# SWITCHED TO PREMIUM TEMPLATE GENERATOR FOR PROFESSIONAL QUALITY
from app.services.template_generator_premium import (
    generate_templates_for_business,
    TemplateGenerationError
)
from app.services.template_generator import (
    delete_existing_templates
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/businesses/{business_id}/templates",
    response_model=TemplateListResponse,
    summary="Get all templates for a business",
    description="Retrieve all AI-generated template variants for a specific business."
)
async def get_business_templates(
    business_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all templates for a business.

    Returns all template variants (1-3) that have been generated for this business.
    """
    # Verify business exists
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.deleted_at.is_(None)
    ).first()

    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )

    # Get all templates
    templates = db.query(Template).filter(
        Template.business_id == business_id
    ).order_by(Template.variant_number).all()

    return TemplateListResponse(
        templates=[TemplateResponse.from_orm(t) for t in templates],
        total=len(templates)
    )


@router.post(
    "/businesses/{business_id}/templates/generate",
    response_model=TemplateListResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate AI templates for a business",
    description="Generate new AI-improved website templates using GPT-4. Generates 1-3 variants."
)
async def generate_templates(
    business_id: uuid.UUID,
    request: TemplateGenerateRequest = TemplateGenerateRequest(),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate AI templates for a business.

    Uses GPT-4 to create modern, responsive website templates based on:
    - Business information (name, category, location, etc.)
    - Existing website evaluation scores
    - Industry best practices

    Generates multiple variants (1-3) with different design approaches.
    """
    # Verify business exists
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.deleted_at.is_(None)
    ).first()

    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )

    # Check if templates already exist
    existing_count = db.query(Template).filter(
        Template.business_id == business_id
    ).count()

    if existing_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Templates already exist for this business. Use the regenerate endpoint to create new ones."
        )

    try:
        # Generate templates
        templates = await generate_templates_for_business(
            business=business,
            db=db,
            num_variants=request.num_variants
        )

        logger.info(f"Generated {len(templates)} templates for business {business_id}")

        return TemplateListResponse(
            templates=[TemplateResponse.from_orm(t) for t in templates],
            total=len(templates)
        )

    except TemplateGenerationError as e:
        logger.error(f"Template generation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate templates: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during template generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during template generation"
        )


@router.post(
    "/businesses/{business_id}/templates/regenerate",
    response_model=TemplateListResponse,
    summary="Regenerate AI templates for a business",
    description="Delete existing templates and generate new ones. Useful for getting fresh designs."
)
async def regenerate_templates(
    business_id: uuid.UUID,
    request: TemplateGenerateRequest = TemplateGenerateRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Regenerate templates for a business.

    Deletes all existing templates and generates new ones with potentially different designs.
    """
    # Verify business exists
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.deleted_at.is_(None)
    ).first()

    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )

    try:
        # Delete existing templates
        await delete_existing_templates(business_id=business_id, db=db)

        # Generate new templates
        templates = await generate_templates_for_business(
            business=business,
            db=db,
            num_variants=request.num_variants
        )

        logger.info(f"Regenerated {len(templates)} templates for business {business_id}")

        return TemplateListResponse(
            templates=[TemplateResponse.from_orm(t) for t in templates],
            total=len(templates)
        )

    except TemplateGenerationError as e:
        logger.error(f"Template regeneration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate templates: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during template regeneration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during template regeneration"
        )


@router.get(
    "/templates/{template_id}",
    response_model=TemplateResponse,
    summary="Get a specific template",
    description="Retrieve a single template by its ID."
)
async def get_template(
    template_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific template by ID"""
    template = db.query(Template).filter(Template.id == template_id).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    return TemplateResponse.from_orm(template)
