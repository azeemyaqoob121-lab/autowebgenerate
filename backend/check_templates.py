"""
Check what templates exist and if they're using ChatGPT
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.models.template import Template
from app.models.business import Business
from sqlalchemy import desc

db = SessionLocal()

print("=" * 80)
print("CHECKING TEMPLATES IN DATABASE")
print("=" * 80)
print()

# Get all templates ordered by most recent
templates = db.query(Template).order_by(desc(Template.generated_at)).limit(10).all()

print(f"Found {len(templates)} recent templates:")
print()

for i, template in enumerate(templates, 1):
    business = db.query(Business).filter(Business.id == template.business_id).first()
    method = template.improvements_made.get('method', 'unknown') if template.improvements_made else 'unknown'
    chatgpt_used = template.improvements_made.get('chatgpt_generated', False) if template.improvements_made else False

    print(f"{i}. Business: {business.name if business else 'Unknown'}")
    print(f"   Template ID: {template.id}")
    print(f"   Method: {method}")
    print(f"   ChatGPT Used: {'YES ✅' if chatgpt_used else 'NO ❌'}")
    print(f"   HTML Size: {len(template.html_content):,} chars")
    print(f"   Generated: {template.generated_at}")
    print()

db.close()
