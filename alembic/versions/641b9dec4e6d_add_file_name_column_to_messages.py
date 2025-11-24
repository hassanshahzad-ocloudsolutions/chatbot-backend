"""add file_name column to messages

Revision ID: 641b9dec4e6d
Revises: ef5eb3b0648d
Create Date: 2025-11-24 17:37:22.584710

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '641b9dec4e6d'
down_revision: Union[str, Sequence[str], None] = 'ef5eb3b0648d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'messages',
        sa.Column('file_name', sa.String(length=255), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('messages', 'file_name')
