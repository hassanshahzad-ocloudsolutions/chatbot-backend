"""add subscription_status(inactive,active,cancel,deleted) to users

Revision ID: a40340b14304
Revises: 3763a9ac5e6b
Create Date: 2025-12-15 18:13:30.751237

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a40340b14304'
down_revision: Union[str, Sequence[str], None] = '3763a9ac5e6b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        'users',
        sa.Column('subscription_status', sa.String(length=20), nullable=False, server_default='inactive')
    )


def downgrade():
    op.drop_column('users', 'subscription_status')
