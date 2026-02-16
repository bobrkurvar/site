"""collection_category_pk

Revision ID: c4c09597d44a
Revises: 5c5d64356f43
Create Date: 2026-02-16 08:41:17.247737

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c4c09597d44a"
down_revision: Union[str, Sequence[str], None] = "5c5d64356f43"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_primary_key(
        "collection_id_category_name_pk",
        "collection_category",
        ["collection_id", "category_name"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
