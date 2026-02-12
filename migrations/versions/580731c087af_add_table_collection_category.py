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
down_revision: Union[str, Sequence[str], None] = 'd0d0439927e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table("collections", "collection_category")
    op.alter_column("collection_category", "name", new_column_name="collection_name")
    op.drop_column("collection_category", "image_path")

    op.create_table(
        "collections",
        sa.Column("name", sa.String(),  primary_key=True),
        sa.Column("image_path", sa.String(), unique=True)
    )

    op.execute(sa.text("""
        INSERT INTO collections (name)
        SELECT DISTINCT collection_name
        FROM collection_category
    """))

    op.create_foreign_key(
        "fk_collection_category_collection_name",
        "collection_category",
        "collections",
        ["collection_name"],
        ["name"],
        ondelete="CASCADE"
    )


def downgrade() -> None:
    op.drop_table("collections")
    op.alter_column("collection_category", "collection_name", new_column_name="name")
    op.rename_table("collection_category", "collections")
    op.add_column("collections", sa.Column("image_path", sa.String(), nullable=True))
