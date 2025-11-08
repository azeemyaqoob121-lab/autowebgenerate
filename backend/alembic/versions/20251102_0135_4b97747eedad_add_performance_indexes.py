"""add_performance_indexes

Revision ID: 4b97747eedad
Revises: 59c59dec0a80
Create Date: 2025-11-02 01:35:35.050139

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b97747eedad'
down_revision: Union[str, None] = '59c59dec0a80'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add performance indexes for query optimization.

    Businesses table indexes:
    - created_at: For chronological sorting
    - deleted_at: For soft delete filtering
    - (deleted_at, created_at): Composite for active businesses sorted by creation date

    Users table indexes:
    - is_active: For filtering active users
    - created_at: For user analytics and reporting
    """
    # Business table indexes
    op.create_index(
        'ix_businesses_created_at',
        'businesses',
        ['created_at'],
        unique=False
    )

    op.create_index(
        'ix_businesses_deleted_at',
        'businesses',
        ['deleted_at'],
        unique=False
    )

    op.create_index(
        'ix_businesses_deleted_at_created_at',
        'businesses',
        ['deleted_at', 'created_at'],
        unique=False
    )

    # User table indexes
    op.create_index(
        'ix_users_is_active',
        'users',
        ['is_active'],
        unique=False
    )

    op.create_index(
        'ix_users_created_at',
        'users',
        ['created_at'],
        unique=False
    )


def downgrade() -> None:
    """
    Remove performance indexes.
    """
    # Drop user table indexes
    op.drop_index('ix_users_created_at', table_name='users')
    op.drop_index('ix_users_is_active', table_name='users')

    # Drop business table indexes
    op.drop_index('ix_businesses_deleted_at_created_at', table_name='businesses')
    op.drop_index('ix_businesses_deleted_at', table_name='businesses')
    op.drop_index('ix_businesses_created_at', table_name='businesses')
