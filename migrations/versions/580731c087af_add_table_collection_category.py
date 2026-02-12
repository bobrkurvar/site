"""add_table_collection_category

Revision ID: 580731c087af
Revises: 82f83a491aea
Create Date: 2026-02-12 08:52:04.838316

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '580731c087af'
down_revision: Union[str, Sequence[str], None] = '82f83a491aea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table("collections", "collection_category")
    op.alter_column("collection_category", "name", new_column_name="collection_name")

    op.create_table(
        "collections",
        sa.Column("name", sa.String(),  primary_key=True),
        sa.Column("image_path", sa.String())

    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
