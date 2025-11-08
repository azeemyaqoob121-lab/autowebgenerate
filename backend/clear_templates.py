"""
Clear Old Templates Script

This script deletes all existing templates from the database
so that new responsive templates will be generated with the updated code.

Run this script once to clear old non-responsive templates.
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal
from app.models import Template
from sqlalchemy import delete

def clear_all_templates():
    """Delete all templates from database"""
    db = SessionLocal()
    try:
        # Count existing templates
        count_before = db.query(Template).count()
        print(f"\n[INFO] Found {count_before} existing templates in database")

        if count_before == 0:
            print("[SUCCESS] No templates to clear. Database is already empty.")
            return

        # Confirm deletion
        confirm = input(f"\n[WARNING] Are you sure you want to delete ALL {count_before} templates? (yes/no): ")

        if confirm.lower() not in ['yes', 'y']:
            print("[CANCELLED] Deletion cancelled")
            return

        # Delete all templates
        print("\n[DELETING] Removing all templates...")
        stmt = delete(Template)
        result = db.execute(stmt)
        db.commit()

        deleted_count = result.rowcount
        count_after = db.query(Template).count()

        print(f"[SUCCESS] Successfully deleted {deleted_count} templates")
        print(f"[INFO] Templates remaining: {count_after}")
        print("\n[FEATURES] Next time you generate templates, they will have:")
        print("   - Full mobile responsiveness (480px, 768px, 1024px breakpoints)")
        print("   - Professional visual design with gradients and shadows")
        print("   - Working mobile navigation menu")
        print("   - Proper logo and image display")
        print("   - Modern glassmorphism effects")
        print("\n[INSTRUCTIONS] To generate new templates:")
        print("   1. Go to your frontend application")
        print("   2. Add or select a business")
        print("   3. Click 'Generate Templates'")
        print("   4. The new responsive template will be created!")

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 70)
    print("  CLEAR OLD NON-RESPONSIVE TEMPLATES")
    print("=" * 70)
    clear_all_templates()
    print("=" * 70)
