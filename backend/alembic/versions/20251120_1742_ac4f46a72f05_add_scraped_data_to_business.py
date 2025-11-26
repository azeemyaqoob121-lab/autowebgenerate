"""add_scraped_data_to_business

Revision ID: ac4f46a72f05
Revises: a1b2c3d4e5f6
Create Date: 2025-11-20 17:42:27.387073

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ac4f46a72f05'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add scraped_data column to businesses table
    op.add_column('businesses', sa.Column('scraped_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    # Remove scraped_data column from businesses table
    op.drop_column('businesses', 'scraped_data')
