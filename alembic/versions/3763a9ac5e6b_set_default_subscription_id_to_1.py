"""Set default subscription_id to 1

Revision ID: 3763a9ac5e6b
Revises: 675308371b58
Create Date: 2025-12-05 14:54:45.302916

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3763a9ac5e6b'
down_revision: Union[str, Sequence[str], None] = '675308371b58'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Set default to 1
    op.alter_column(
        'users',                    # table name
        'subscription_id',           # column name
        server_default=sa.text('1'),
        existing_type=sa.Integer,
        existing_nullable=True
    )



def downgrade():
    # Revert default to NULL
    op.alter_column(
        'users',
        'subscription_id',
        server_default=None,
        existing_type=sa.Integer,
        existing_nullable=True
    )
