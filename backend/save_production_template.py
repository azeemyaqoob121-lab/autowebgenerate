"""Save the fixed production-ready template to database."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.business import Business
from app.models.template import Template

db = SessionLocal()

try:
    # Read the fixed template
    with open("template_cc_electrical_PRODUCTION_READY.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Get business
    business = db.query(Business).filter(
        Business.name == "C.C Electrical & Sons"
    ).first()

    # Delete old templates
    old_templates = db.query(Template).filter(Template.business_id == business.id).all()
    for t in old_templates:
        db.delete(t)
    db.commit()

    # Save new template
    template = Template(
        business_id=business.id,
        variant_number=1,
        html_content=html,
        css_content="",
        js_content=None,
        improvements_made={"method": "production_ready_with_tailwind_fix"},
        generated_at=__import__('datetime').datetime.utcnow()
    )

    db.add(template)
    db.commit()

    print(f"SUCCESS! Saved production template to database")
    print(f"Template ID: {template.id}")
    print(f"Size: {len(html):,} characters")
    print(f"File: template_cc_electrical_PRODUCTION_READY.html")

finally:
    db.close()
