"""
Database seeding script for performance testing.

Generates 1000+ realistic business records with varied locations, categories,
and scores for benchmarking query performance.

Usage:
    python scripts/seed_database.py --count 1000
    python scripts/seed_database.py --clear  # Clear all data
"""
import sys
import argparse
from pathlib import Path
import random
import uuid
from datetime import datetime, timedelta

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Business, User
from app.utils.security import hash_password

# UK locations for realistic data
UK_LOCATIONS = [
    "London", "Manchester", "Birmingham", "Leeds", "Glasgow",
    "Liverpool", "Newcastle", "Sheffield", "Bristol", "Leicester",
    "Edinburgh", "Cardiff", "Belfast", "Nottingham", "Southampton",
    "Brighton", "Plymouth", "Reading", "Cambridge", "Oxford",
    "York", "Bath", "Norwich", "Exeter", "Chester"
]

# Business categories
BUSINESS_CATEGORIES = [
    "Plumbing", "Electrical", "Construction", "Landscaping",
    "Roofing", "Painting & Decorating", "Carpentry", "Heating & Cooling",
    "Cleaning Services", "Pest Control", "Locksmith", "Glazing",
    "Flooring", "Kitchen Fitting", "Bathroom Fitting", "Property Maintenance",
    "Handyman Services", "Security Systems", "Fire Protection", "Fencing"
]

# Business name templates
BUSINESS_NAMES = [
    "{category} {suffix}", "{location} {category}", "{adjective} {category}",
    "{name}'s {category}", "{location} {adjective} {category}"
]

NAME_ADJECTIVES = [
    "Professional", "Quality", "Reliable", "Expert", "Premier",
    "Elite", "Superior", "Trusted", "Local", "Family"
]

NAME_SUFFIXES = [
    "Services", "Solutions", "Ltd", "Specialists", "Pros",
    "Experts", "Group", "& Co", "Contractors", "Services Ltd"
]

COMPANY_NAMES = [
    "Smith", "Jones", "Brown", "Taylor", "Wilson",
    "Davies", "Evans", "Thomas", "Roberts", "Johnson"
]


def generate_email(business_name: str) -> str:
    """Generate a realistic email address"""
    domain_name = business_name.lower().replace(" ", "").replace("'", "")[:15]
    domains = ["co.uk", "com", "org.uk"]
    return f"contact@{domain_name}.{random.choice(domains)}"


def generate_phone() -> str:
    """Generate a realistic UK phone number"""
    area_codes = ["020", "0121", "0161", "0113", "0114", "0117", "0131", "0141", "0151", "0191"]
    return f"{random.choice(area_codes)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"


def generate_website(business_name: str) -> str:
    """Generate a realistic website URL"""
    domain_name = business_name.lower().replace(" ", "").replace("'", "")[:20]
    return f"https://www.{domain_name}-{uuid.uuid4().hex[:6]}.co.uk"


def generate_business_name(category: str, location: str) -> str:
    """Generate a realistic business name"""
    template = random.choice(BUSINESS_NAMES)
    return template.format(
        category=category,
        location=location,
        adjective=random.choice(NAME_ADJECTIVES),
        name=random.choice(COMPANY_NAMES),
        suffix=random.choice(NAME_SUFFIXES)
    )


def generate_description(category: str, location: str) -> str:
    """Generate a realistic business description"""
    templates = [
        f"Professional {category.lower()} services in {location} and surrounding areas. Over 10 years of experience.",
        f"Trusted {category.lower()} specialists serving {location}. Fully insured and certified.",
        f"Quality {category.lower()} solutions for residential and commercial clients in {location}.",
        f"Expert {category.lower()} contractors based in {location}. Free quotes and competitive rates.",
        f"Family-run {category.lower()} business serving {location} since 2010. No job too small."
    ]
    return random.choice(templates)


def generate_address(location: str) -> str:
    """Generate a realistic UK address"""
    street_num = random.randint(1, 999)
    streets = ["High Street", "Church Road", "Station Road", "Main Street", "Mill Lane"]
    postcodes = ["M1 1AA", "B1 1BB", "L1 1CC", "LE1 1DD", "S1 1EE"]
    return f"{street_num} {random.choice(streets)}, {location}, {random.choice(postcodes)}"


def create_test_user(db: Session) -> User:
    """Create a test user for authentication testing"""
    # Check if test user already exists
    existing_user = db.query(User).filter(User.email == "test@autoweb.com").first()
    if existing_user:
        print("Test user already exists")
        return existing_user

    test_user = User(
        id=uuid.uuid4(),
        email="test@autoweb.com",
        hashed_password=hash_password("testpassword123"),
        is_active=True,
        created_at=datetime.utcnow()
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    print("Created test user: test@autoweb.com / testpassword123")
    return test_user


def seed_businesses(db: Session, count: int = 1000):
    """
    Seed the database with realistic business records.

    Args:
        db: Database session
        count: Number of businesses to create (default: 1000)
    """
    print(f"Seeding {count} businesses...")

    businesses = []
    for i in range(count):
        # Random category and location
        category = random.choice(BUSINESS_CATEGORIES)
        location = random.choice(UK_LOCATIONS)

        # Generate business data
        business_name = generate_business_name(category, location)

        # Create business with varied scores (weighted towards lower scores)
        # 60% low scores (0-60), 30% medium (61-80), 10% high (81-100)
        score_range = random.choices(
            [(0, 60), (61, 80), (81, 100)],
            weights=[60, 30, 10]
        )[0]
        score = random.randint(*score_range)

        # Random creation date within last year
        days_ago = random.randint(0, 365)
        created_at = datetime.utcnow() - timedelta(days=days_ago)

        # 10% soft deleted
        deleted_at = None
        if random.random() < 0.1:
            deleted_at = created_at + timedelta(days=random.randint(1, 30))

        business = Business(
            id=uuid.uuid4(),
            name=business_name,
            email=generate_email(business_name),
            phone=generate_phone(),
            address=generate_address(location),
            website_url=generate_website(business_name),
            category=category,
            description=generate_description(category, location),
            location=location,
            score=score,
            created_at=created_at,
            updated_at=created_at,
            deleted_at=deleted_at
        )
        businesses.append(business)

        # Commit in batches of 100 for better performance
        if (i + 1) % 100 == 0:
            db.bulk_save_objects(businesses)
            db.commit()
            businesses = []
            print(f"  Seeded {i + 1}/{count} businesses...")

    # Commit remaining businesses
    if businesses:
        db.bulk_save_objects(businesses)
        db.commit()

    print(f"✓ Successfully seeded {count} businesses")


def clear_all_data(db: Session):
    """Clear all data from the database"""
    print("Clearing all data from database...")

    # Delete in correct order due to foreign keys
    db.query(Business).delete()
    db.query(User).delete()
    db.commit()

    print("✓ All data cleared")


def get_database_stats(db: Session):
    """Print current database statistics"""
    total_businesses = db.query(Business).count()
    active_businesses = db.query(Business).filter(Business.deleted_at.is_(None)).count()
    deleted_businesses = db.query(Business).filter(Business.deleted_at.isnot(None)).count()
    total_users = db.query(User).count()

    print("\n" + "="*50)
    print("DATABASE STATISTICS")
    print("="*50)
    print(f"Total Businesses:  {total_businesses:,}")
    print(f"Active Businesses: {active_businesses:,}")
    print(f"Deleted Businesses: {deleted_businesses:,}")
    print(f"Total Users:       {total_users:,}")
    print("="*50 + "\n")


def main():
    """Main entry point for seed script"""
    parser = argparse.ArgumentParser(description="Seed database with test data")
    parser.add_argument(
        "--count",
        type=int,
        default=1000,
        help="Number of businesses to create (default: 1000)"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear all existing data before seeding"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show database statistics only (no seeding)"
    )

    args = parser.parse_args()

    # Create database session
    db = SessionLocal()

    try:
        # Show stats if requested
        if args.stats:
            get_database_stats(db)
            return

        # Clear data if requested
        if args.clear:
            clear_all_data(db)

        # Create test user (commented out due to bcrypt issue - use registration endpoint instead)
        # create_test_user(db)
        print("Note: Test user creation skipped. Use POST /api/auth/register to create users.")

        # Seed businesses
        seed_businesses(db, count=args.count)

        # Show final statistics
        get_database_stats(db)

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
