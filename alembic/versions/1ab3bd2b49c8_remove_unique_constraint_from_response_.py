"""Remove unique constraint from response column

Revision ID: 1ab3bd2b49c8
Revises: 76e553394fc1
Create Date: 2025-04-29 18:59:58.224822

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1ab3bd2b49c8'
down_revision: Union[str, None] = '76e553394fc1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # commands to remove the unique constraint
    with op.batch_alter_table("exercice", schema=None) as batch_op:
        batch_op.alter_column("response", existing_type=sa.String(length=255), nullable=False)
        batch_op.drop_constraint("ix_exercice_response", type_="unique")


def downgrade():
    # commands to re-add the unique constraint (if needed)
    with op.batch_alter_table("exercice", schema=None) as batch_op:
        batch_op.create_unique_constraint("ix_exercice_response", ["response"])
