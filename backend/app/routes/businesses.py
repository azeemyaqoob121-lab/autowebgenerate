"""Business CRUD API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
import uuid

from app.database import get_db
from app.models import User, Template, Business
from app.schemas.business import (
    BusinessCreate,
    BusinessUpdate,
    BusinessResponse,
    BusinessListResponse,
    BusinessFilters,
    BusinessDiscoveryRequest,
    BusinessDiscoveryResponse
)
from app.services import business_service
from app.services.places_service import get_places_service
from app.services.evaluation_service import try_auto_evaluate
# SWITCHED TO PREMIUM TEMPLATE GENERATOR FOR PROFESSIONAL QUALITY DURING AUTO-DISCOVERY
from app.services.template_generator_premium import generate_templates_for_business
from app.utils.security import get_current_user
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


router = APIRouter()


@router.get(
    "/stats",
    summary="Get dashboard statistics",
    description="Get statistics for dashboard: total businesses, qualified leads, templates generated"
)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics.

    Returns:
    - total_businesses: Total number of businesses in database
    - qualified_leads: Number of businesses with score < 70
    - templates_generated: Total number of AI templates generated
    """
    try:
        # Get total businesses count (exclude deleted)
        total_businesses = db.query(func.count(Business.id)).filter(
            Business.deleted_at.is_(None)
        ).scalar() or 0

        # Get qualified leads count (score < 70 and not deleted)
        qualified_leads = db.query(func.count(Business.id)).filter(
            Business.deleted_at.is_(None),
            Business.score < 70,
            Business.score.isnot(None)
        ).scalar() or 0

        # Get total templates generated
        templates_generated = db.query(func.count(Template.id)).scalar() or 0

        return {
            "total_businesses": total_businesses,
            "qualified_leads": qualified_leads,
            "templates_generated": templates_generated
        }
    except Exception as e:
        logger.error(f"Failed to fetch dashboard stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard stats: {str(e)}"
        )


@router.get(
    "",
    response_model=BusinessListResponse,
    summary="List all businesses",
    description="Get paginated list of businesses with optional filtering and sorting"
)
async def list_businesses(
    score_min: Optional[int] = Query(None, ge=0, le=100, description="Minimum score filter"),
    score_max: Optional[int] = Query(None, ge=0, le=100, description="Maximum score filter"),
    location: Optional[str] = Query(None, description="Filter by location"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search across name, description, category"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Offset from start"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of businesses with filtering and sorting.

    Requires authentication.

    Filters:
    - **score_min/score_max**: Filter by evaluation score range
    - **location**: Filter by location (case-insensitive partial match)
    - **category**: Filter by category (case-insensitive partial match)
    - **search**: Text search across name, description, category, location

    Pagination:
    - **limit**: Number of items per page (1-100, default 50)
    - **offset**: Offset from start (default 0)

    Sorting:
    - **sort_by**: Field to sort by (default: created_at)
    - **sort_order**: asc or desc (default: desc)
    """
    # Create filters object
    filters = BusinessFilters(
        score_min=score_min,
        score_max=score_max,
        location=location,
        category=category,
        search=search,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order
    )

    # Get businesses with filters
    businesses, total = business_service.get_businesses(db, filters)

    # Convert to response models
    business_responses = []
    for business in businesses:
        response = BusinessResponse.from_orm(business)
        # Set computed fields
        response.has_evaluation = len(business.evaluations) > 0 if hasattr(business, 'evaluations') else False
        response.has_template = len(business.templates) > 0 if hasattr(business, 'templates') else False
        business_responses.append(response)

    # Calculate pagination flags
    has_next = (offset + limit) < total
    has_prev = offset > 0

    return BusinessListResponse(
        items=business_responses,
        total=total,
        limit=limit,
        offset=offset,
        has_next=has_next,
        has_prev=has_prev
    )


@router.get(
    "/{business_id}",
    response_model=BusinessResponse,
    summary="Get business by ID",
    description="Get detailed information about a specific business"
)
async def get_business(
    business_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific business by ID.

    Requires authentication.

    Returns:
    - Full business details including evaluation and template status
    - 404 if business not found or has been deleted
    """
    business = business_service.get_business_by_id(db, business_id)

    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with ID {business_id} not found"
        )

    # Convert to response model
    response = BusinessResponse.from_orm(business)
    response.has_evaluation = len(business.evaluations) > 0 if hasattr(business, 'evaluations') else False
    response.has_template = len(business.templates) > 0 if hasattr(business, 'templates') else False

    return response


@router.post(
    "",
    response_model=BusinessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new business",
    description="Manually create a new business entry"
)
async def create_business(
    business_data: BusinessCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new business.

    Requires authentication.

    Validates:
    - Website URL must be unique (not already registered)
    - All required fields present and valid

    Returns:
    - 201 Created with business details
    - 400 Bad Request if website URL already exists
    """
    # Check if website URL already exists
    existing_business = business_service.get_business_by_website(
        db,
        str(business_data.website_url)
    )

    if existing_business:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Business with website URL {business_data.website_url} already exists"
        )

    # Create new business
    new_business = business_service.create_business(db, business_data)

    # Convert to response
    response = BusinessResponse.from_orm(new_business)
    response.has_evaluation = False
    response.has_template = False

    return response


@router.post(
    "/discover",
    response_model=BusinessDiscoveryResponse,
    status_code=status.HTTP_200_OK,
    summary="Discover real businesses",
    description="Discover real UK businesses via Google Places API with automatic evaluation and template generation"
)
async def discover_businesses(
    discovery_request: BusinessDiscoveryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Discover real businesses from Google Places API.

    This endpoint:
    1. Searches Google Places API for real UK businesses by location and category
    2. Saves discovered businesses to the database (skips duplicates)
    3. Automatically evaluates each business website using Google Lighthouse
    4. Automatically generates AI templates for businesses with score < 70 using GPT-4

    All operations are automatic - no manual "Evaluate" button needed!

    Requires authentication and valid GOOGLE_API_KEY configured.

    Parameters:
    - **location**: UK location (e.g., "London", "Manchester", "Birmingham")
    - **category**: Business category/niche (e.g., "plumber", "restaurant", "electrician")
    - **max_results**: Maximum number of businesses to discover (1-20, default: 10)
    - **auto_evaluate**: Enable automatic evaluation (default: true)

    Returns:
    - Statistics about discovered, saved, evaluated businesses
    - Number of AI templates generated for low-scoring websites
    - List of all discovered businesses with their data
    """
    logger.info(
        f"Discovering businesses: location='{discovery_request.location}', "
        f"category='{discovery_request.category}', max_results={discovery_request.max_results}"
    )

    try:
        # Step 1: Discover businesses from Google Places API
        places_service = get_places_service()
        discovered_data = places_service.search_businesses(
            location=discovery_request.location,
            category=discovery_request.category,
            max_results=discovery_request.max_results
        )

        logger.info(f"Discovered {len(discovered_data)} businesses from Google Places API")

        if not discovered_data:
            logger.warning(f"No businesses found for {discovery_request.category} in {discovery_request.location}")
            return BusinessDiscoveryResponse(
                discovered=0,
                saved=0,
                evaluated=0,
                templates_generated=0,
                businesses=[]
            )

        # Step 2: Save businesses to database
        saved_businesses = []
        saved_count = 0

        for business_data in discovered_data:
            try:
                # Skip if no website URL
                if not business_data.get("website_url"):
                    logger.debug(f"Skipping business '{business_data.get('name')}' - no website URL")
                    continue

                # Check if business already exists
                existing = business_service.get_business_by_website(db, business_data["website_url"])
                if existing:
                    logger.debug(f"Business already exists: {business_data['name']}")
                    saved_businesses.append(existing)
                    saved_count += 1
                    continue

                # Create business in database
                business_create = BusinessCreate(
                    name=business_data["name"],
                    email=None,  # Google Places doesn't provide email
                    phone=business_data.get("phone"),
                    address=business_data.get("address"),
                    website_url=business_data["website_url"],
                    category=business_data.get("category", discovery_request.category),
                    description=f"{business_data.get('category', discovery_request.category)} business in {discovery_request.location}",
                    location=business_data.get("city", discovery_request.location)
                )

                new_business = business_service.create_business(db, business_create)
                saved_businesses.append(new_business)
                saved_count += 1

                logger.info(f"Saved new business: {business_data['name']} ({business_data['website_url']})")

            except Exception as e:
                logger.error(f"Failed to save business {business_data.get('name')}: {str(e)}")
                continue

        logger.info(f"Saved {saved_count} new businesses to database")

        # Step 3: Automatically evaluate businesses (if enabled)
        evaluated_count = 0
        templates_generated_count = 0

        if discovery_request.auto_evaluate:
            for business in saved_businesses:
                try:
                    # Try to evaluate (will skip if already evaluated recently)
                    evaluation_success = try_auto_evaluate(db, business.id)

                    if evaluation_success:
                        evaluated_count += 1

                        # Refresh business to get updated score
                        db.refresh(business)

                        # Step 4: Generate AI template if score < 70
                        if business.score is not None and business.score < 70:
                            logger.info(f"Business '{business.name}' has score {business.score} < 70, generating AI template...")

                            try:
                                # Check if template already exists
                                existing_templates = db.query(Template).filter_by(
                                    business_id=business.id
                                ).first()

                                if not existing_templates:
                                    templates = await generate_templates_for_business(
                                        business=business,
                                        db=db,
                                        num_variants=1
                                    )
                                    templates_generated_count += len(templates)
                                    logger.info(f"Generated {len(templates)} AI template(s) for business '{business.name}'")

                            except Exception as e:
                                logger.error(f"Failed to generate template for business {business.name}: {str(e)}")

                except Exception as e:
                    logger.error(f"Failed to evaluate business {business.name}: {str(e)}")
                    continue

        logger.info(
            f"Discovery complete: discovered={len(discovered_data)}, saved={saved_count}, "
            f"evaluated={evaluated_count}, templates_generated={templates_generated_count}"
        )

        # Step 5: Filter businesses - only include those with score < 70
        # These are the businesses that need improvement!
        filtered_businesses = []
        for business in saved_businesses:
            db.refresh(business)  # Ensure we have latest data

            # Only include businesses with score < 70 (or no score yet)
            if business.score is not None and business.score >= 70:
                logger.info(f"Filtering out business '{business.name}' with score {business.score} >= 70")
                continue

            response = BusinessResponse.from_orm(business)
            response.has_evaluation = len(business.evaluations) > 0 if hasattr(business, 'evaluations') else False
            response.has_template = len(business.templates) > 0 if hasattr(business, 'templates') else False
            filtered_businesses.append(response)

        logger.info(f"Filtered results: {len(filtered_businesses)} businesses with score < 70")
        business_responses = filtered_businesses

        return BusinessDiscoveryResponse(
            discovered=len(discovered_data),
            saved=saved_count,
            evaluated=evaluated_count,
            templates_generated=templates_generated_count,
            businesses=business_responses
        )

    except Exception as e:
        logger.error(f"Business discovery failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Business discovery failed: {str(e)}"
        )


@router.put(
    "/{business_id}",
    response_model=BusinessResponse,
    summary="Update business",
    description="Update an existing business"
)
async def update_business(
    business_id: uuid.UUID,
    business_data: BusinessUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing business.

    Requires authentication.

    - Only provided fields will be updated
    - If website_url is changed, it must still be unique
    - Returns 404 if business not found

    Returns:
    - Updated business details
    """
    # Check business exists
    existing_business = business_service.get_business_by_id(db, business_id)

    if not existing_business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with ID {business_id} not found"
        )

    # If website_url is being changed, check uniqueness
    if business_data.website_url:
        url_conflict = business_service.get_business_by_website(
            db,
            str(business_data.website_url),
            exclude_id=business_id
        )

        if url_conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Website URL {business_data.website_url} is already used by another business"
            )

    # Update business
    updated_business = business_service.update_business(db, business_id, business_data)

    # Convert to response
    response = BusinessResponse.from_orm(updated_business)
    response.has_evaluation = len(updated_business.evaluations) > 0 if hasattr(updated_business, 'evaluations') else False
    response.has_template = len(updated_business.templates) > 0 if hasattr(updated_business, 'templates') else False

    return response


@router.delete(
    "/{business_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete business",
    description="Soft delete a business (sets deleted_at timestamp)"
)
async def delete_business(
    business_id: uuid.UUID,
    hard_delete: bool = Query(False, description="Permanently delete (WARNING: irreversible)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a business (soft delete by default).

    Requires authentication.

    By default, performs soft delete (sets deleted_at timestamp).
    Business can be restored by clearing deleted_at field.

    Use hard_delete=true query parameter for permanent deletion (WARNING: irreversible).

    Returns:
    - 204 No Content on success
    - 404 if business not found
    """
    if hard_delete:
        # Permanent deletion
        success = business_service.hard_delete_business(db, business_id)
    else:
        # Soft delete
        success = business_service.delete_business(db, business_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with ID {business_id} not found"
        )

    return None  # 204 No Content
