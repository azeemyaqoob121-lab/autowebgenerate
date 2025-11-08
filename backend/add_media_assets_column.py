"""Add media_assets column to templates table"""
import sys
from sqlalchemy import create_engine, text
from app.config import settings

def add_column():
    """Add media_assets JSONB column to templates table"""
    print("Connecting to database...")
    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        try:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'templates'
                AND column_name = 'media_assets'
            """))

            if result.fetchone():
                print("✓ Column 'media_assets' already exists!")
                return

            # Add the column
            print("Adding media_assets column...")
            conn.execute(text("""
                ALTER TABLE templates
                ADD COLUMN media_assets JSONB
            """))
            conn.commit()
            print("✓ Column 'media_assets' added successfully!")

        except Exception as e:
            print(f"✗ Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    add_column()
