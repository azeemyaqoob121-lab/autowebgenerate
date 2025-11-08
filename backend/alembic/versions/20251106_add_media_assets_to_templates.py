"""add_media_assets_to_templates

Revision ID: a1b2c3d4e5f6
Revises: 4b97747eedad
Create Date: 2025-11-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '4b97747eedad'
branch_labels = None
depends_on = None


def upgrade():
    """Add media_assets JSONB column to templates table"""
    op.add_column('templates', sa.Column('media_assets', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade():
    """Remove media_assets column from templates table"""
    op.drop_column('templates', 'media_assets')
