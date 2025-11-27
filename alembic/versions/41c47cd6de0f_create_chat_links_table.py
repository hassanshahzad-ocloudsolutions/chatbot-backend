"""create chat_links table

Revision ID: 41c47cd6de0f
Revises: 380d62431e71
Create Date: 2025-11-27 15:46:08.004418

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '41c47cd6de0f'
down_revision: Union[str, Sequence[str], None] = '380d62431e71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():


    # Create chat_links table
    op.create_table(
        'chat_links',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('chat_id', sa.Integer, sa.ForeignKey('chats.id', ondelete='CASCADE'), nullable=False),
        sa.Column('read_only', sa.Boolean(), nullable=False, server_default=sa.text('TRUE')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
    )


def downgrade():
    # Drop chat_links table
    op.drop_table('chat_links')
