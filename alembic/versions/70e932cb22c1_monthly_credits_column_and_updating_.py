"""monthly_credits_column_and_updating_daily_credits_in_subscription_plans

Revision ID: 70e932cb22c1
Revises: fbf841aad474
Create Date: 2025-12-16 15:38:18.982407

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '70e932cb22c1'
down_revision: Union[str, Sequence[str], None] = 'fbf841aad474'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add monthly_credits column, default 0
    op.add_column('subscription_plans', sa.Column('monthly_credits', sa.Integer(), nullable=False, server_default='0'))

    # Update existing plans
    op.execute(
        """
        UPDATE subscription_plans
        SET daily_credits = 10, monthly_credits = 0
        WHERE name = 'Free';
        """
    )
    op.execute(
        """
        UPDATE subscription_plans
        SET daily_credits = 0, monthly_credits = 500
        WHERE name = 'Pro';
        """
    )
    op.execute(
        """
        UPDATE subscription_plans
        SET daily_credits = 0, monthly_credits = 700
        WHERE name = 'Enterprise';
        """
    )


def downgrade():
    # Remove the column in downgrade
    op.drop_column('subscription_plans', 'monthly_credits')

    # Optionally reset daily_credits to previous state if needed
    op.execute(
        """
        UPDATE subscription_plans
        SET daily_credits = 0
        WHERE name IN ('Free', 'Pro', 'Enterprise');
        """
    )
