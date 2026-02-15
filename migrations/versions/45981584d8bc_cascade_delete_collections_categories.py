"""cascade_delete_collections_categories

Revision ID: 45981584d8bc
Revises: 580731c087af
Create Date: 2026-02-12 20:29:44.392238

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '45981584d8bc'
down_revision: Union[str, Sequence[str], None] = '580731c087af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Удаляем старые FK
    op.drop_constraint(
        "collections_category_name_fkey",
        "collection_category",
        type_="foreignkey"
    )
    op.drop_constraint(
        "fk_collection_category_collection_name",
        "collection_category",
        type_="foreignkey"
    )

    # Создаём новые с CASCADE
    op.create_foreign_key(
        "fk_collection_category_collection",
        "collection_category",
        "collections",
        ["collection_name"],
        ["name"],
        ondelete="CASCADE"
    )

    op.create_foreign_key(
        "fk_collection_category_category",
        "collection_category",
        "categories",
        ["category_name"],
        ["name"],
        ondelete="CASCADE"
    )


def downgrade():
    op.drop_constraint("fk_collection_category_collection", "collection_category", type_="foreignkey")
    op.drop_constraint("fk_collection_category_category", "collection_category", type_="foreignkey")

    op.create_foreign_key(
        "collection_category_collection_name_fkey",
        "collection_category",
        "collections",
        ["collection_name"],
        ["name"]
    )

    op.create_foreign_key(
        "collection_category_category_name_fkey",
        "collection_category",
        "categories",
        ["category_name"],
        ["name"]
    )