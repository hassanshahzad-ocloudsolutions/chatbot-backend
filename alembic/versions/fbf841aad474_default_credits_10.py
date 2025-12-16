"""default_credits_10

Revision ID: fbf841aad474
Revises: a40340b14304
Create Date: 2025-12-16 15:36:33.133255

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fbf841aad474'
down_revision: Union[str, Sequence[str], None] = 'a40340b14304'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade()->None:
    op.alter_column(
        'users',
        'credits_left',
        server_default=sa.text('10'),
        existing_type=sa.Integer
    )

def downgrade()->None:
    op.alter_column(
        'users',
        'credits_left',
        server_default=sa.text('5'),
        existing_type=sa.Integer
    )