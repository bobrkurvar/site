"""add_category_id

Revision ID: 0ce71f9da427
Revises: db61c58b90c1
Create Date: 2026-09-08 18:51:58.606563

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0ce71f9da427'
down_revision: Union[str, Sequence[str], None] = 'db61c58b90c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Новый идентификатор категории.
    op.execute("""
        ALTER TABLE categories
        ADD COLUMN id SERIAL
    """)

    # 2. Новые FK-колонки пока nullable.
    op.add_column(
        "catalog",
        sa.Column("category_id", sa.Integer(), nullable=True),
    )

    op.add_column(
        "collection_category",
        sa.Column("category_id", sa.Integer(), nullable=True),
    )

    # 3. Переносим существующие связи name -> id.
    op.execute("""
        UPDATE catalog AS c
        SET category_id = cat.id
        FROM categories AS cat
        WHERE c.category_name = cat.name
    """)

    op.execute("""
        UPDATE collection_category AS cc
        SET category_id = cat.id
        FROM categories AS cat
        WHERE cc.category_name = cat.name
    """)

    # 4. Теперь NULL быть не должно.
    op.alter_column(
        "catalog",
        "category_id",
        nullable=False,
    )

    op.alter_column(
        "collection_category",
        "category_id",
        nullable=False,
    )

    # 5. Убираем старые FK на categories.name.
    op.drop_constraint(
        "fk_catalog_types",
        "catalog",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_collection_category_category",
        "collection_category",
        type_="foreignkey",
    )

    # 6. Старый PK collection_category содержит category_name,
    # поэтому его надо удалить до удаления колонки.
    op.drop_constraint(
        "collection_id_category_name_pk",
        "collection_category",
        type_="primary",
    )

    # 7. Меняем PK categories: name -> id.
    op.drop_constraint(
        "types_pkey",
        "categories",
        type_="primary",
    )

    op.create_primary_key(
        "categories_pkey",
        "categories",
        ["id"],
    )

    # name больше не PK, но названия категорий должны оставаться уникальными.
    op.create_unique_constraint(
        "uq_categories_name",
        "categories",
        ["name"],
    )

    # 8. Создаём новые FK по id.
    op.create_foreign_key(
        "fk_catalog_category",
        "catalog",
        "categories",
        ["category_id"],
        ["id"],
    )

    op.create_foreign_key(
        "fk_collection_category_category",
        "collection_category",
        "categories",
        ["category_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # 9. Новый составной PK.
    op.create_primary_key(
        "collection_id_category_id_pk",
        "collection_category",
        ["collection_id", "category_id"],
    )

    # 10. Старые строковые FK больше не нужны.
    op.drop_column("catalog", "category_name")
    op.drop_column("collection_category", "category_name")


def downgrade() -> None:
    pass
