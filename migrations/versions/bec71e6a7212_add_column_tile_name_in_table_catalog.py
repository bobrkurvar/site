"""add_column_tile_name_in_table_catalog

Revision ID: bec71e6a7212
Revises:
Create Date: 2025-12-01 18:17:54.187718

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from fastapi_admin.widgets.filters import ForeignKey

# revision identifiers, used by Alembic.
revision: str = "bec71e6a7212"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column("catalog", sa.Column("type_name", sa.String, nullable=True))

    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
        UPDATE catalog
        SET type_name = 'Tile'
        WHERE type_name IS NULL
    """
        )
    )

    op.alter_column("catalog", "type_name", nullable=False)

    op.create_foreign_key(
        "fk_catalog_types", "catalog", "types", ["type_name"], ["name"]
    )


def downgrade():
    # Откат: удаляем внешний ключ и столбец
    pass
