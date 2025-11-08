"""Fix database column - add media_assets to templates table"""
import sys
from sqlalchemy import create_engine, text, inspect
from app.config import settings

def main():
    print("=" * 60)
    print("DATABASE COLUMN FIX SCRIPT")
    print("=" * 60)
    print()

    # Step 1: Connect to database
    print("Step 1: Connecting to database...")
    try:
        engine = create_engine(settings.DATABASE_URL)
        print(f"✓ Connected to: {settings.DATABASE_URL[:50]}...")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        sys.exit(1)

    # Step 2: Check existing columns
    print("\nStep 2: Checking existing columns in 'templates' table...")
    try:
        inspector = inspect(engine)
        columns = inspector.get_columns('templates')
        column_names = [col['name'] for col in columns]

        print(f"✓ Found {len(columns)} columns:")
        for col_name in column_names:
            print(f"  - {col_name}")

        if 'media_assets' in column_names:
            print("\n✓ Column 'media_assets' ALREADY EXISTS!")
            print("  No action needed.")
            return
        else:
            print("\n⚠ Column 'media_assets' NOT FOUND")
            print("  Will add it now...")

    except Exception as e:
        print(f"✗ Error checking columns: {e}")
        sys.exit(1)

    # Step 3: Add the column
    print("\nStep 3: Adding 'media_assets' JSONB column...")
    try:
        with engine.connect() as conn:
            # Begin transaction
            trans = conn.begin()

            try:
                # Add the column
                conn.execute(text("""
                    ALTER TABLE templates
                    ADD COLUMN media_assets JSONB
                """))

                # Commit transaction
                trans.commit()
                print("✓ Column added successfully!")

            except Exception as e:
                trans.rollback()
                print(f"✗ Error adding column: {e}")
                raise

    except Exception as e:
        print(f"✗ Transaction failed: {e}")
        sys.exit(1)

    # Step 4: Verify column was added
    print("\nStep 4: Verifying column was added...")
    try:
        inspector = inspect(engine)
        columns = inspector.get_columns('templates')
        column_names = [col['name'] for col in columns]

        if 'media_assets' in column_names:
            print("✓ VERIFICATION SUCCESSFUL!")
            print("  Column 'media_assets' is now in the database.")
        else:
            print("✗ VERIFICATION FAILED!")
            print("  Column was not added. Manual intervention required.")
            sys.exit(1)

    except Exception as e:
        print(f"✗ Verification error: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("SUCCESS! Database schema updated.")
    print("=" * 60)
    print("\nNext step: Restart your backend server to pick up the changes.")

if __name__ == "__main__":
    main()
