"""create_subscription_plans_table

Revision ID: 65b4c26a6248
Revises: 
Create Date: 2025-11-21 12:09:33.615363

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision: str = '65b4c26a6248'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'subscription_plans',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, unique=True, nullable=False),
        sa.Column('daily_credits', sa.Integer, nullable=False),
        sa.Column('price_cents', sa.Integer, nullable=False, default=0),
        sa.Column('stripe_price_id', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow)
    )

def downgrade():
    op.drop_table('subscription_plans')