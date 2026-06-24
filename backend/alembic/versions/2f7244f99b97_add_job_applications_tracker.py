"""add job applications tracker

Revision ID: 2f7244f99b97
Revises: 743a99eda1a3
Create Date: 2026-06-05 00:06:29.172938
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '2f7244f99b97'
down_revision: Union[str, Sequence[str], None] = '743a99eda1a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'job_applications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('job_title', sa.String(), nullable=False),
        sa.Column('company', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='Inbox'),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('date_applied', sa.Date(), nullable=True),
        sa.Column('interview_date', sa.Date(), nullable=True),
        sa.Column('deadline', sa.Date(), nullable=True),
        sa.Column('keywords', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('link', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_job_applications_user_id', 'job_applications', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_job_applications_user_id', 'job_applications', if_exists=True)
    op.drop_table('job_applications')