"""merge multiple heads

Revision ID: 5ff1349a531a
Revises: 843cdeb35da5, bae6ceca1408
Create Date: 2025-12-17 10:47:02.589297

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ff1349a531a'
down_revision: Union[str, Sequence[str], None] = ('843cdeb35da5', 'bae6ceca1408')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
