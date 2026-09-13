"""rename_catalog_to_tiles

Revision ID: 4b5792bc0886
Revises: 0ce71f9da427
Create Date: 2026-09-09 16:03:18.034495

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b5792bc0886'
down_revision: Union[str, Sequence[str], None] = '0ce71f9da427'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table("catalog", "tiles")


def downgrade() -> None:
    pass
