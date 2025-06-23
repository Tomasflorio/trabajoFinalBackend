"""fix_thematic_enum_values

Revision ID: 2db7ef2609c1
Revises: bba4bb7b56ce
Create Date: 2025-06-23 14:29:03.557356

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2db7ef2609c1'
down_revision: Union[str, None] = 'bba4bb7b56ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Actualizar el enum thematic para incluir los nuevos valores
    op.execute("ALTER TABLE content MODIFY COLUMN thematic ENUM('technology', 'science', 'literature', 'art') NOT NULL")


def downgrade() -> None:
    """Downgrade schema."""
    # Revertir a los valores originales del enum
    op.execute("ALTER TABLE content MODIFY COLUMN thematic ENUM('TBD') NOT NULL")
