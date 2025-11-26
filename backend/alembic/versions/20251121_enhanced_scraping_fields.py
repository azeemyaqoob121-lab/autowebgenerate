"""enhanced_scraping_fields

Adds specific fields for enhanced HTML scraping and component preservation.
This migration supports Story 4.10: Enhanced HTML Scraping and AI-Driven Template Modernization.

Revision ID: e7f8g9h0i1j2
Revises: ac4f46a72f05
Create Date: 2025-11-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e7f8g9h0i1j2'
down_revision: Union[str, None] = 'ac4f46a72f05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add enhanced scraping fields to businesses table.

    Fields added:
    - scraped_html: Complete HTML document
    - scraped_css: Extracted inline and internal CSS
    - external_css_urls: Array of external CSS file URLs
    - image_urls: Array of all image URLs
    - logo_urls: Array of logo URLs (subset of images)
    - video_urls: Array of video URLs and iframe embeds
    - map_embeds: Array of map iframe embeds
    - color_palette: Array of hex color codes extracted from CSS
    - component_count: Number of major HTML sections/components
    - component_structure: Detailed component structure analysis
    - scraping_completed_at: Timestamp when scraping finished
    - scraping_error: Error message if scraping failed
    """
    # Add TEXT fields for raw HTML and CSS
    op.add_column('businesses',
        sa.Column('scraped_html', sa.Text(), nullable=True,
                  doc="Complete HTML document from business website"))

    op.add_column('businesses',
        sa.Column('scraped_css', sa.Text(), nullable=True,
                  doc="Extracted inline and internal CSS"))

    # Add JSONB fields for structured asset data
    op.add_column('businesses',
        sa.Column('external_css_urls', postgresql.JSONB(), nullable=True,
                  doc="Array of external CSS file URLs"))

    op.add_column('businesses',
        sa.Column('image_urls', postgresql.JSONB(), nullable=True,
                  doc="Array of all image src URLs"))

    op.add_column('businesses',
        sa.Column('logo_urls', postgresql.JSONB(), nullable=True,
                  doc="Array of logo image URLs (subset of image_urls)"))

    op.add_column('businesses',
        sa.Column('video_urls', postgresql.JSONB(), nullable=True,
                  doc="Array of video src URLs and iframe embeds"))

    op.add_column('businesses',
        sa.Column('map_embeds', postgresql.JSONB(), nullable=True,
                  doc="Array of map iframe embeds (Google Maps, etc.)"))

    op.add_column('businesses',
        sa.Column('color_palette', postgresql.JSONB(), nullable=True,
                  doc="Array of hex color codes extracted from CSS"))

    # Add component structure fields
    op.add_column('businesses',
        sa.Column('component_count', sa.Integer(), nullable=True,
                  doc="Count of major HTML sections/components"))

    op.add_column('businesses',
        sa.Column('component_structure', postgresql.JSONB(), nullable=True,
                  doc="Detailed structure of HTML components"))

    # Add scraping metadata fields
    op.add_column('businesses',
        sa.Column('scraping_completed_at', sa.DateTime(), nullable=True,
                  doc="Timestamp when scraping completed successfully"))

    op.add_column('businesses',
        sa.Column('scraping_error', sa.Text(), nullable=True,
                  doc="Error message if scraping failed"))

    # Add index for performance on scraping_completed_at
    op.create_index('idx_businesses_scraping_completed',
                    'businesses', ['scraping_completed_at'])


def downgrade() -> None:
    """Remove enhanced scraping fields from businesses table"""
    # Drop index first
    op.drop_index('idx_businesses_scraping_completed', table_name='businesses')

    # Drop columns in reverse order
    op.drop_column('businesses', 'scraping_error')
    op.drop_column('businesses', 'scraping_completed_at')
    op.drop_column('businesses', 'component_structure')
    op.drop_column('businesses', 'component_count')
    op.drop_column('businesses', 'color_palette')
    op.drop_column('businesses', 'map_embeds')
    op.drop_column('businesses', 'video_urls')
    op.drop_column('businesses', 'logo_urls')
    op.drop_column('businesses', 'image_urls')
    op.drop_column('businesses', 'external_css_urls')
    op.drop_column('businesses', 'scraped_css')
    op.drop_column('businesses', 'scraped_html')
