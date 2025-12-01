"""add_column_tile_name_in_table_catalog

Revision ID: bec71e6a7212
Revises: 
Create Date: 2025-12-01 18:17:54.187718

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from fastapi_admin.widgets.filters import ForeignKey

# revision identifiers, used by Alembic.
revision: str = 'bec71e6a7212'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1. Добавляем новый столбец, временно nullable
    op.add_column(
        "catalog",
        sa.Column("type_name", sa.String, nullable=True)
    )
    op.drop_column("types", "tile_id")

    conn = op.get_bind()
    conn.execute(sa.text("""
        UPDATE catalog
        SET type_name = 'Плитка'
        WHERE type_name IS NULL
    """))

    op.alter_column("catalog", "type_name", nullable=False)

    # 4. Добавляем FOREIGN KEY
    op.create_foreign_key(
        "fk_catalog_types",
        "catalog", "types",
        ["type_name"], ["name"]
    )


def downgrade():
    # Откат: удаляем внешний ключ и столбец
    op.drop_constraint("fk_child_parent", "child", type_="foreignkey")
    op.drop_column("child", "parent_id")
