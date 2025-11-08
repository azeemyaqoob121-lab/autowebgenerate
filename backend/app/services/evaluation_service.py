"""Evaluation service layer for website quality assessment"""
from sqlalchemy.orm import Session
from typing import Optional
import uuid
from datetime import datetime

from app.models import Evaluation, Business
from app.utils.logging_config import get_logger
from app.services.lighthouse_service import get_lighthouse_service

logger = get_logger(__name__)


def get_evaluation_by_business_id(db: Session, business_id: uuid.UUID) -> Optional[Evaluation]:
    """
    Get the latest evaluation for a business.

    Args:
        db: Database session
        business_id: Business UUID

    Returns:
        Latest Evaluation object or None
    """
    return db.query(Evaluation).filter(
        Evaluation.business_id == business_id
    ).order_by(Evaluation.evaluated_at.desc()).first()


def create_evaluation(db: Session, business_id: uuid.UUID) -> Evaluation:
    """
    Create a new evaluation for a business using real Lighthouse API.

    This uses Google PageSpeed Insights API to run real Lighthouse audits.
    Falls back to mock data if API is unavailable.

    Args:
        db: Database session
        business_id: Business UUID to evaluate

    Returns:
        Created Evaluation object

    Raises:
        ValueError: If business not found
    """
    # Verify business exists
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise ValueError(f"Business with ID {business_id} not found")

    if not business.website_url:
        raise ValueError(f"Business {business_id} has no website URL to evaluate")

    logger.info(f"Creating evaluation for business {business_id} ({business.name})")
    logger.info(f"Running Lighthouse audit for URL: {business.website_url}")

    # Get Lighthouse service and run audit (real data only, no fallback)
    lighthouse = get_lighthouse_service()
    audit_result = lighthouse.run_audit_with_validation(str(business.website_url))

    # Extract scores
    performance_score = audit_result["performance_score"]
    seo_score = audit_result["seo_score"]
    accessibility_score = audit_result["accessibility_score"]
    aggregate_score = audit_result["aggregate_score"]
    lighthouse_data = audit_result["lighthouse_data"]

    # Add metadata
    lighthouse_data["website_url"] = str(business.website_url)
    lighthouse_data["business_name"] = business.name
    lighthouse_data["is_real_data"] = audit_result.get("success", False)

    # Create new evaluation
    new_evaluation = Evaluation(
        id=uuid.uuid4(),
        business_id=business_id,
        performance_score=performance_score,
        seo_score=seo_score,
        accessibility_score=accessibility_score,
        aggregate_score=aggregate_score,
        lighthouse_data=lighthouse_data,
        evaluated_at=datetime.utcnow()
    )

    db.add(new_evaluation)

    # Update business score
    business.score = int(aggregate_score)
    business.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(new_evaluation)

    logger.info(
        f"Evaluation created with REAL Lighthouse data for business {business_id}: "
        f"aggregate_score={aggregate_score:.2f}, "
        f"performance={performance_score:.2f}, "
        f"seo={seo_score:.2f}, "
        f"accessibility={accessibility_score:.2f}"
    )

    return new_evaluation


def try_auto_evaluate(db: Session, business_id: uuid.UUID) -> bool:
    """
    Try to automatically evaluate a business if it doesn't have recent evaluation.

    This is used for auto-evaluation when businesses are listed.
    Silently fails if evaluation cannot be performed.

    Args:
        db: Database session
        business_id: Business UUID

    Returns:
        True if evaluation succeeded, False otherwise
    """
    try:
        # Check if business already has a recent evaluation (within last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)

        recent_eval = db.query(Evaluation).filter(
            Evaluation.business_id == business_id,
            Evaluation.evaluated_at >= week_ago
        ).first()

        if recent_eval:
            return True  # Already has recent evaluation

        # Try to create evaluation
        create_evaluation(db, business_id)
        return True
    except Exception as e:
        # Silently fail - don't break the business listing
        logger.debug(f"Auto-evaluation failed for business {business_id}: {str(e)}")
        return False
