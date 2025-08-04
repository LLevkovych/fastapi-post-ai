"""Add is_auto_reply field to comments

Revision ID: add_is_auto_reply_to_comments
Revises: 8d70ef889eaf
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_is_auto_reply_to_comments'
down_revision = '8d70ef889eaf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_auto_reply column to comments table
    op.add_column('comments', sa.Column('is_auto_reply', sa.Boolean(), nullable=False, server_default='0'))


def downgrade() -> None:
    # Remove is_auto_reply column from comments table
    op.drop_column('comments', 'is_auto_reply') 