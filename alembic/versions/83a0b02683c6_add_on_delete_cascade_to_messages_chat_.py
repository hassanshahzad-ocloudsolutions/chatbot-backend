"""Add ON DELETE CASCADE to messages.chat_id

Revision ID: 83a0b02683c6
Revises: c9e7a2b37ee3
Create Date: 2025-11-28 15:03:15.952540

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '83a0b02683c6'
down_revision: Union[str, Sequence[str], None] = 'c9e7a2b37ee3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Drop existing FK
    op.drop_constraint('messages_chat_id_fkey', 'messages', type_='foreignkey')
    # Create new FK with ON DELETE CASCADE
    op.create_foreign_key(
        'messages_chat_id_fkey',
        'messages',
        'chats',
        ['chat_id'],
        ['id'],
        ondelete='CASCADE'
    )

def downgrade():
    # Drop FK with cascade
    op.drop_constraint('messages_chat_id_fkey', 'messages', type_='foreignkey')
    # Recreate original FK without cascade
    op.create_foreign_key(
        'messages_chat_id_fkey',
        'messages',
        'chats',
        ['chat_id'],
        ['id']
    )

