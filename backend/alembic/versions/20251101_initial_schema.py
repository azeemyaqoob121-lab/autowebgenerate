"""Initial schema

Revision ID: 001_initial
Revises:
Create Date: 2025-11-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create businesses table
    op.create_table(
        'businesses',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('address', sa.String(500), nullable=True),
        sa.Column('website_url', sa.String(500), nullable=False),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('score', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
    )

    # Create indexes for businesses table
    op.create_index('ix_businesses_id', 'businesses', ['id'])
    op.create_index('ix_businesses_website_url', 'businesses', ['website_url'], unique=True)
    op.create_index('ix_businesses_category', 'businesses', ['category'])
    op.create_index('ix_businesses_location', 'businesses', ['location'])
    op.create_index('ix_businesses_score', 'businesses', ['score'])
    op.create_index('ix_business_score_location', 'businesses', ['score', 'location'])
    op.create_index('ix_business_category_score', 'businesses', ['category', 'score'])

    # Create evaluations table
    op.create_table(
        'evaluations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('business_id', UUID(as_uuid=True), sa.ForeignKey('businesses.id', ondelete='CASCADE'), nullable=False),
        sa.Column('performance_score', sa.Float, nullable=False),
        sa.Column('seo_score', sa.Float, nullable=False),
        sa.Column('accessibility_score', sa.Float, nullable=False),
        sa.Column('aggregate_score', sa.Float, nullable=False),
        sa.Column('lighthouse_data', JSONB, nullable=False),
        sa.Column('evaluated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
    )

    # Create indexes for evaluations table
    op.create_index('ix_evaluations_id', 'evaluations', ['id'])
    op.create_index('ix_evaluations_business_id', 'evaluations', ['business_id'])
    op.create_index('ix_evaluations_aggregate_score', 'evaluations', ['aggregate_score'])
    op.create_index('ix_evaluations_evaluated_at', 'evaluations', ['evaluated_at'])

    # Create evaluation_problems table
    # Using VARCHAR for enum columns - the actual ENUM constraint will be enforced by models
    op.create_table(
        'evaluation_problems',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('evaluation_id', UUID(as_uuid=True), sa.ForeignKey('evaluations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('problem_type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
    )

    # Add check constraints to enforce enum values at database level
    op.execute("ALTER TABLE evaluation_problems ADD CONSTRAINT check_problem_type CHECK (problem_type IN ('performance', 'seo', 'accessibility', 'best-practices'))")
    op.execute("ALTER TABLE evaluation_problems ADD CONSTRAINT check_severity CHECK (severity IN ('critical', 'major', 'minor'))")

    # Create indexes for evaluation_problems table
    op.create_index('ix_evaluation_problems_id', 'evaluation_problems', ['id'])
    op.create_index('ix_evaluation_problems_evaluation_id', 'evaluation_problems', ['evaluation_id'])
    op.create_index('ix_evaluation_problems_problem_type', 'evaluation_problems', ['problem_type'])
    op.create_index('ix_evaluation_problems_severity', 'evaluation_problems', ['severity'])

    # Create templates table
    op.create_table(
        'templates',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('business_id', UUID(as_uuid=True), sa.ForeignKey('businesses.id', ondelete='CASCADE'), nullable=False),
        sa.Column('html_content', sa.Text, nullable=False),
        sa.Column('css_content', sa.Text, nullable=False),
        sa.Column('js_content', sa.Text, nullable=True),
        sa.Column('improvements_made', JSONB, nullable=False, server_default='{}'),
        sa.Column('variant_number', sa.Integer, nullable=False),
        sa.Column('generated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
    )

    # Create indexes for templates table
    op.create_index('ix_templates_id', 'templates', ['id'])
    op.create_index('ix_templates_business_id', 'templates', ['business_id'])
    op.create_index('ix_templates_generated_at', 'templates', ['generated_at'])
    op.create_index('ix_template_business_variant', 'templates', ['business_id', 'variant_number'])


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table('templates')
    op.drop_table('evaluation_problems')
    op.drop_table('evaluations')
    op.drop_table('businesses')

    # Drop enum types
    op.execute('DROP TYPE IF EXISTS problemseverity')
    op.execute('DROP TYPE IF EXISTS problemtype')
