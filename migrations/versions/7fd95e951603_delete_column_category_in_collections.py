"""delete_column_category_in_collections

Revision ID: 7fd95e951603
Revises: 8ca2e012f82d
Create Date: 2025-12-09 17:08:56.131991

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7fd95e951603'
down_revision: Union[str, Sequence[str], None] = '8ca2e012f82d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('collections', 'category')


def downgrade() -> None:
    """Downgrade schema."""
    pass
