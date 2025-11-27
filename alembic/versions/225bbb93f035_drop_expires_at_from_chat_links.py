"""drop expires_at from chat_links

Revision ID: 225bbb93f035
Revises: 41c47cd6de0f
Create Date: 2025-11-27 17:31:14.031006

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '225bbb93f035'
down_revision: Union[str, Sequence[str], None] = '41c47cd6de0f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Drop the column
    op.drop_column('chat_links', 'expires_at')

def downgrade():
    # Re-add the column in case of rollback
    op.add_column(
        'chat_links',
        sa.Column('expires_at', sa.DateTime(), nullable=True)
    )