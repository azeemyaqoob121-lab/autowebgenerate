"""Check the actual HTML content in the database"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Template

db: Session = SessionLocal()

try:
    # Get the latest template
    template = db.query(Template).filter(
        Template.business_id == "639ace15-ebce-4332-98ce-2e49382fd424"
    ).order_by(Template.generated_at.desc()).first()

    if template:
        print(f"Template ID: {template.id}")
        print(f"Generated: {template.generated_at}")
        print(f"HTML Length: {len(template.html_content)}")
        print()

        html = template.html_content
        html_lower = html.lower()

        # Check structure
        print("=== STRUCTURE CHECKS ===")
        print(f"Has <html>: {'<html' in html_lower}")
        print(f"Has <head>: {'<head' in html_lower}")
        print(f"Has </head>: {'</head>' in html_lower}")
        print(f"Has <body>: {'<body' in html_lower}")
        print(f"Has </body>: {'</body>' in html_lower}")
        print(f"Has </html>: {'</html>' in html_lower}")
        print()

        # Find where body should be
        head_end = html_lower.find('</head>')
        if head_end > 0:
            print("=== CONTENT AFTER </head> (first 500 chars) ===")
            after_head = html[head_end:head_end+500]
            print(repr(after_head))
            print()

        # Check end of HTML
        print("=== LAST 300 CHARACTERS ===")
        print(repr(html[-300:]))
        print()

        # Check if there's content between head and html closing
        if '</head>' in html_lower and '</html>' in html_lower:
            head_end_idx = html_lower.find('</head>') + 7
            html_end_idx = html_lower.find('</html>')
            between = html[head_end_idx:html_end_idx]
            print(f"=== CONTENT BETWEEN </head> and </html> ({len(between)} chars) ===")
            if len(between) < 500:
                print(repr(between))
            else:
                print(f"First 200 chars: {repr(between[:200])}")
                print(f"Last 200 chars: {repr(between[-200:])}")
    else:
        print("No template found!")

finally:
    db.close()
