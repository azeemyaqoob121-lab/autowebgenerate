"""
Check what templates are actually in the database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.template import Template
from app.models.business import Business

db = SessionLocal()

try:
    # Get all templates
    templates = db.query(Template).all()

    print(f"\nTotal templates in database: {len(templates)}\n")

    for template in templates:
        business = db.query(Business).filter(Business.id == template.business_id).first()

        print(f"Template ID: {template.id}")
        print(f"Business: {business.name if business else 'Unknown'} ({template.business_id})")
        print(f"Variant: {template.variant_number}")
        print(f"HTML length: {len(template.html_content):,} characters")
        print(f"Generated at: {template.generated_at}")
        print(f"Has content: {'YES' if len(template.html_content) > 100 else 'NO - EMPTY!'}")
        print(f"First 200 chars: {template.html_content[:200]}")
        print("-" * 80)
        print()

finally:
    db.close()
