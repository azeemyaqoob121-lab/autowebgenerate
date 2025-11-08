"""Business service layer with CRUD operations"""
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import Optional, List, Tuple
from datetime import datetime
import uuid

from app.models import Business
from app.schemas.business import BusinessCreate, BusinessUpdate, BusinessFilters


def get_businesses(
    db: Session,
    filters: BusinessFilters
) -> Tuple[List[Business], int]:
    """
    Get paginated list of businesses with filters.

    Args:
        db: Database session
        filters: BusinessFilters with pagination and filter params

    Returns:
        Tuple of (businesses list, total count)
    """
    # Base query excluding soft-deleted records
    query = db.query(Business).filter(Business.deleted_at.is_(None))

    # Apply filters
    if filters.score_min is not None:
        query = query.filter(Business.score >= filters.score_min)

    if filters.score_max is not None:
        query = query.filter(Business.score <= filters.score_max)

    if filters.location:
        query = query.filter(Business.location.ilike(f"%{filters.location}%"))

    if filters.category:
        query = query.filter(Business.category.ilike(f"%{filters.category}%"))

    # Text search across multiple fields
    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.filter(
            or_(
                Business.name.ilike(search_term),
                Business.description.ilike(search_term),
                Business.category.ilike(search_term),
                Business.location.ilike(search_term)
            )
        )

    # Get total count before pagination
    total = query.count()

    # Apply sorting
    sort_column = getattr(Business, filters.sort_by, Business.created_at)
    if filters.sort_order == "desc":
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    query = query.order_by(sort_column)

    # Apply pagination
    businesses = query.offset(filters.offset).limit(filters.limit).all()

    return businesses, total


def get_business_by_id(db: Session, business_id: uuid.UUID) -> Optional[Business]:
    """
    Get a single business by ID.

    Args:
        db: Database session
        business_id: Business UUID

    Returns:
        Business object or None if not found or deleted
    """
    return db.query(Business).filter(
        Business.id == business_id,
        Business.deleted_at.is_(None)
    ).first()


def get_business_by_website(db: Session, website_url: str, exclude_id: Optional[uuid.UUID] = None) -> Optional[Business]:
    """
    Get a business by website URL (for uniqueness check).

    Args:
        db: Database session
        website_url: Website URL to check
        exclude_id: Optional business ID to exclude (for updates)

    Returns:
        Business object or None
    """
    query = db.query(Business).filter(
        Business.website_url == str(website_url),
        Business.deleted_at.is_(None)
    )

    if exclude_id:
        query = query.filter(Business.id != exclude_id)

    return query.first()


def create_business(db: Session, business_data: BusinessCreate) -> Business:
    """
    Create a new business.

    Args:
        db: Database session
        business_data: BusinessCreate schema

    Returns:
        Created Business object
    """
    new_business = Business(
        id=uuid.uuid4(),
        name=business_data.name,
        email=business_data.email,
        phone=business_data.phone,
        address=business_data.address,
        website_url=str(business_data.website_url),
        category=business_data.category,
        description=business_data.description,
        location=business_data.location,
        score=None,  # Will be set after evaluation
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(new_business)
    db.commit()
    db.refresh(new_business)

    return new_business


def update_business(
    db: Session,
    business_id: uuid.UUID,
    business_data: BusinessUpdate
) -> Optional[Business]:
    """
    Update a business.

    Args:
        db: Database session
        business_id: Business UUID
        business_data: BusinessUpdate schema with fields to update

    Returns:
        Updated Business object or None if not found
    """
    business = get_business_by_id(db, business_id)

    if not business:
        return None

    # Update only provided fields
    update_data = business_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field == "website_url" and value:
            setattr(business, field, str(value))
        else:
            setattr(business, field, value)

    business.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(business)

    return business


def delete_business(db: Session, business_id: uuid.UUID) -> bool:
    """
    Soft delete a business (set deleted_at timestamp).

    Args:
        db: Database session
        business_id: Business UUID

    Returns:
        True if deleted, False if not found
    """
    business = get_business_by_id(db, business_id)

    if not business:
        return False

    business.deleted_at = datetime.utcnow()
    db.commit()

    return True


def hard_delete_business(db: Session, business_id: uuid.UUID) -> bool:
    """
    Permanently delete a business from database.

    Args:
        db: Database session
        business_id: Business UUID

    Returns:
        True if deleted, False if not found

    Warning: This permanently removes the business and all related data.
    Use soft delete instead unless absolutely necessary.
    """
    business = db.query(Business).filter(Business.id == business_id).first()

    if not business:
        return False

    db.delete(business)
    db.commit()

    return True
