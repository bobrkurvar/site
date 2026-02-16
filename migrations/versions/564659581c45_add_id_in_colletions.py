"""add_id_in_colletions

Revision ID: 564659581c45
Revises: 45981584d8bc
Create Date: 2026-02-15 15:56:22.457398

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "564659581c45"
down_revision: Union[str, Sequence[str], None] = "45981584d8bc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # 1. Удаляем старый FK
    op.drop_constraint(
        "fk_collection_category_collection", "collection_category", type_="foreignkey"
    )

    # 2. Переименовываем старую таблицу
    op.rename_table("collections", "old_collections")

    # 3. Создаём новую таблицу
    op.create_table(
        "collections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), unique=True, nullable=False),
        sa.Column("image_path", sa.String(), unique=True, nullable=False),
    )

    # 4. Переносим данные
    op.execute(
        """
        INSERT INTO collections (name, image_path)
        SELECT name, image_path
        FROM old_collections
    """
    )

    # 5. Добавляем новый столбец
    op.add_column(
        "collection_category", sa.Column("collection_id", sa.Integer(), nullable=True)
    )

    # 6. Заполняем его
    op.execute(
        """
        UPDATE collection_category cc
        SET collection_id = (
            SELECT id
            FROM collections c
            WHERE c.name = cc.collection_name
        )
    """
    )

    # 7. Делаем NOT NULL
    op.alter_column("collection_category", "collection_id", nullable=False)

    # 8. Удаляем старый столбец
    op.drop_column("collection_category", "collection_name")

    # 9. Создаём новый FK
    op.create_foreign_key(
        "fk_collection_category_collection",
        "collection_category",
        "collections",
        ["collection_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # 10. Удаляем старую таблицу
    op.drop_table("old_collections")


def downgrade() -> None:

    # 1. Переименовываем текущую таблицу
    op.rename_table("collections", "new_collections")

    # 2. Возвращаем старую таблицу
    op.rename_table("old_collections", "collections")

    # 3. Добавляем обратно collection_name
    op.add_column(
        "collection_category", sa.Column("collection_name", sa.String(), nullable=True)
    )

    # 4. Заполняем его
    op.execute(
        """
        UPDATE collection_category cc
        SET collection_name = (
            SELECT c.name
            FROM new_collections c
            WHERE c.id = cc.collection_id
        )
    """
    )

    # 5. Делаем NOT NULL
    op.alter_column("collection_category", "collection_name", nullable=False)

    # 6. Удаляем FK по id
    op.drop_constraint(
        "fk_collection_category_collection", "collection_category", type_="foreignkey"
    )

    # 7. Удаляем collection_id
    op.drop_column("collection_category", "collection_id")

    # 8. Создаём старый FK
    op.create_foreign_key(
        "fk_collection_category_collection",
        "collection_category",
        "collections",
        ["collection_name"],
        ["name"],
        ondelete="CASCADE",
    )

    # 9. Удаляем новую таблицу
    op.drop_table("new_collections")
