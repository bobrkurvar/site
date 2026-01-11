"""add_column_category_to_collections

Revision ID: 0f8770cb6427
Revises: 2ed0d48bed3d
Create Date: 2025-12-31 09:43:38.733473

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = "0f8770cb6427"
down_revision: Union[str, Sequence[str], None] = "2ed0d48bed3d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def extract_quoted_word(name: str) -> str | None:
    parts = name.split('"')
    if len(parts) >= 3:
        return parts[1].lower()
    return None


def upgrade() -> None:
    bind = op.get_bind()

    # 1️⃣ Создаём новую таблицу
    op.create_table(
        "collections_new",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("category_name", sa.String(), nullable=False),
        sa.Column("image_path", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("name", "category_name"),
        sa.ForeignKeyConstraint(["category_name"], ["categories.name"]),
    )

    # 2️⃣ Загружаем старые коллекции
    collections = bind.execute(
        text("SELECT name, image_path FROM collections")
    ).fetchall()

    collections_map = {row.name.lower(): row.image_path for row in collections}

    # 3️⃣ Загружаем товары
    products = bind.execute(
        text(
            """
            SELECT name, category_name
            FROM catalog
        """
        )
    ).fetchall()

    # 4️⃣ Собираем уникальные пары (collection, category)
    found = set()

    for product in products:
        product_name = extract_quoted_word(product.name)
        if product_name:
            for collection_name in collections_map:
                if collection_name in product_name:
                    found.add((collection_name, product.category_name))

    # 5️⃣ Вставляем в новую таблицу
    for collection_name, category_name in found:
        bind.execute(
            text(
                """
                INSERT INTO collections_new (name, category_name, image_path)
                VALUES (:name, :category_name, :image_path)
                ON CONFLICT DO NOTHING
            """
            ),
            {
                "name": collection_name,
                "category_name": category_name,
                "image_path": collections_map[collection_name],
            },
        )

    # 6️⃣ Удаляем старую таблицу и переименовываем новую
    op.drop_table("collections")
    op.rename_table("collections_new", "collections")


def downgrade() -> None:
    bind = op.get_bind()

    # 1️⃣ Восстанавливаем старую таблицу
    op.create_table(
        "collections_old",
        sa.Column("name", sa.String(), primary_key=True),
        sa.Column("image_path", sa.String(), nullable=False),
    )

    # 2️⃣ Переносим уникальные коллекции обратно
    bind.execute(
        text(
            """
            INSERT INTO collections_old (name, image_path)
            SELECT DISTINCT name, image_path
            FROM collections
        """
        )
    )

    # 3️⃣ Удаляем новую таблицу
    op.drop_table("collections")

    # 4️⃣ Возвращаем старое имя
    op.rename_table("collections_old", "collections")
