"""add_is_archive_column_in_chats_table

Revision ID: c9e7a2b37ee3
Revises: 225bbb93f035
Create Date: 2025-11-28 11:23:17.653302

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9e7a2b37ee3'
down_revision: Union[str, Sequence[str], None] = '225bbb93f035'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('chats', sa.Column('is_archive',sa.Boolean(), server_default=sa.false(), nullable=False))

def downgrade() -> None:
    op.drop_column('chats', 'is_archive')
