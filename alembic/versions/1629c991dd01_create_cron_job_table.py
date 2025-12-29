"""create cron_job table

Revision ID: 1629c991dd01
Revises: 70e932cb22c1
Create Date: 2025-12-29 16:36:27.323583

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1629c991dd01'
down_revision: Union[str, Sequence[str], None] = '70e932cb22c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cron_job",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.String, nullable=False),
        sa.Column(
            "creation_time",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("next_run_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("task_path", sa.String(), nullable=False),
        sa.Column(
            "status",
            sa.String(),
            nullable=False,
            server_default="active",
        ),
        sa.UniqueConstraint("user_id", name="uq_cron_job_user_id"),
    )

    # Foreign key constraint
    op.create_foreign_key(
        "fk_cron_job_user",
        "cron_job",
        "users",
        ["user_id"],
        ["uid"],
        ondelete="CASCADE",
    )


def downgrade():
    op.drop_constraint("fk_cron_job_user", "cron_job", type_="foreignkey")
    op.drop_constraint("uq_cron_job_user_id", "cron_job", type_="unique")
    op.drop_table("cron_job")
