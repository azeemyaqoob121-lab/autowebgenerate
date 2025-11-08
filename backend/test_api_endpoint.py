"""Test API endpoint to debug 422 error"""
import sys
import codecs
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.config import settings
from app.models import Business, Template
from app.schemas.template import TemplateResponse, TemplateListResponse

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Create database connection
engine = create_engine(settings.DATABASE_URL)
db = Session(bind=engine)

try:
    # Get the business ID that's causing the error
    business_id = "1de27bf7-7591-45fd-9910-7a4037685009"

    print(f"Checking business: {business_id}")

    # Check if business exists
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.deleted_at.is_(None)
    ).first()

    if not business:
        print("❌ Business not found or deleted")
        sys.exit(1)

    print(f"✓ Business found: {business.name}")

    # Get templates
    templates = db.query(Template).filter(
        Template.business_id == business_id
    ).order_by(Template.variant_number).all()

    print(f"✓ Found {len(templates)} template(s)")

    # Try to convert each template to response schema
    for i, template in enumerate(templates, 1):
        print(f"\nTemplate {i}:")
        print(f"  - ID: {template.id}")
        print(f"  - Variant: {template.variant_number}")
        print(f"  - HTML length: {len(template.html_content) if template.html_content else 0}")
        print(f"  - CSS length: {len(template.css_content) if template.css_content else 0}")
        print(f"  - improvements_made type: {type(template.improvements_made)}")
        print(f"  - improvements_made value: {template.improvements_made}")
        print(f"  - media_assets: {bool(template.media_assets)}")

        # Try to convert to TemplateResponse
        try:
            response = TemplateResponse.model_validate(template)
            print(f"  ✓ Successfully validated!")
        except Exception as e:
            print(f"  ❌ Validation failed: {e}")
            print(f"  Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()

finally:
    db.close()
