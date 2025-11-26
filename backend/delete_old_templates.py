"""
Delete all old templates so fresh ChatGPT ones will be generated
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.models.template import Template

db = SessionLocal()

print("=" * 80)
print("DELETING OLD TEMPLATES")
print("=" * 80)
print()

# Get all templates
templates = db.query(Template).all()

print(f"Found {len(templates)} templates to delete")
print()

for template in templates:
    method = template.improvements_made.get('method', 'unknown') if template.improvements_made else 'unknown'
    print(f"Deleting template {template.id} (method: {method})")
    db.delete(template)

db.commit()

print()
print(f"Deleted {len(templates)} old templates!")
print()
print("Now when you regenerate, you'll get fresh ChatGPT modern designs!")
print("=" * 80)

db.close()
