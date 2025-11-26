"""
Script to delete ALL templates from database.
This forces regeneration with the new modernization code.

Run this to clear old templates that were generated before the fix.
"""

from app.database import SessionLocal
from app.models import Template
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_all_templates():
    """Delete all templates from database"""
    db = SessionLocal()
    try:
        # Count existing templates
        count = db.query(Template).count()
        logger.info(f"Found {count} existing templates in database")

        if count == 0:
            logger.info("No templates to delete")
            return

        # Delete all templates
        db.query(Template).delete()
        db.commit()

        logger.info(f"✅ Successfully deleted {count} templates")
        logger.info("Now you can regenerate templates and they will use the new modernization code")

    except Exception as e:
        logger.error(f"Error deleting templates: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("CLEARING ALL TEMPLATES FROM DATABASE")
    print("This will force regeneration with new modernization code")
    print("="*60 + "\n")

    response = input("Are you sure you want to delete ALL templates? (yes/no): ")
    if response.lower() == "yes":
        clear_all_templates()
    else:
        print("Cancelled")
