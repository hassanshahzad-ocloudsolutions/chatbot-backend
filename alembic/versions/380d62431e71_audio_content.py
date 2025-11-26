"""audio_content

Revision ID: 380d62431e71
Revises: 641b9dec4e6d
Create Date: 2025-11-26 16:08:39.199158

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '380d62431e71'
down_revision: Union[str, Sequence[str], None] = '641b9dec4e6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add audio_content column to messages table (for storing transcribed text)."""
    op.add_column(
        'messages',
        sa.Column('audio_content', sa.Text, nullable=True)
    )

def downgrade() -> None:
    """Remove audio_content column from messages table."""
    op.drop_column('messages', 'audio_content')
