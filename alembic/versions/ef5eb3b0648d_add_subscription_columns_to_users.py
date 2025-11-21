"""add_subscription_columns_to_users

Revision ID: ef5eb3b0648d
Revises: 65b4c26a6248
Create Date: 2025-11-21 12:13:24.370228

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision: str = 'ef5eb3b0648d'
down_revision: Union[str, Sequence[str], None] = '65b4c26a6248'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('users', sa.Column('subscription_id', sa.Integer, sa.ForeignKey('subscription_plans.id'), nullable=True))
    op.add_column('users', sa.Column('credits_left', sa.Integer, nullable=False, server_default="0"))
    op.add_column('users', sa.Column('last_reset', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))
    op.add_column('users', sa.Column('stripe_subscription_id', sa.String, nullable=True))

def downgrade():
    op.drop_column('users', 'stripe_subscription_id')
    op.drop_column('users', 'last_reset')
    op.drop_column('users', 'credits_left')
    op.drop_column('users', 'subscription_id')