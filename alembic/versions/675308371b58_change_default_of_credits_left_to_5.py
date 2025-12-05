"""Change default of credits_left to 5

Revision ID: 675308371b58
Revises: 83a0b02683c6
Create Date: 2025-12-05 14:52:16.996717

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '675308371b58'
down_revision: Union[str, Sequence[str], None] = '83a0b02683c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Set default to 5
    op.alter_column(
        'users',                     # table name
        'credits_left',               # column name
        server_default=sa.text('5'), # new default
        existing_type=sa.Integer
    )

def downgrade():
    # Revert default back to 0
    op.alter_column(
        'users',
        'credits_left',
        server_default=sa.text('0'),
        existing_type=sa.Integer
    )
