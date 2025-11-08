"""User Model for Authentication"""
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid as uuid_lib

from app.database import Base


class User(Base):
    """
    User model for authentication and authorization.

    Stores user credentials and authentication state.
    Each user can create scraping jobs (relationship defined in Epic 2).

    Attributes:
        id: Unique identifier (UUID)
        email: User's email address (unique, indexed)
        hashed_password: Bcrypt hashed password (never store plain passwords)
        is_active: Account active status (for soft delete/suspension)
        created_at: Account creation timestamp
    """
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid_lib.uuid4,
        nullable=False,
        index=True
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="User email address (used for login)"
    )

    hashed_password = Column(
        String(255),
        nullable=False,
        doc="Bcrypt hashed password (never log or expose this)"
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        doc="Account active status (false = suspended/deleted)"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="Account creation timestamp"
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, is_active={self.is_active})>"
