"""merge_heads

Revision ID: 354bcab37610
Revises: 8a9cd703d56e, f047afcd9402
Create Date: 2025-06-04 11:40:07.485354

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '354bcab37610'
down_revision: Union[str, None] = ('8a9cd703d56e', 'f047afcd9402')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
