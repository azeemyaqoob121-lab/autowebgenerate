import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.models.template import Template
from sqlalchemy import desc

db = SessionLocal()
templates = db.query(Template).order_by(desc(Template.generated_at)).limit(3).all()

print(f"Found {len(templates)} templates:")
print()

for t in templates:
    method = t.improvements_made.get('method', 'unknown') if t.improvements_made else 'unknown'
    chatgpt = t.improvements_made.get('chatgpt_generated', False) if t.improvements_made else False
    print(f"ID: {t.id}")
    print(f"Method: {method}")
    print(f"ChatGPT: {chatgpt}")
    print(f"Generated: {t.generated_at}")
    print()

db.close()
