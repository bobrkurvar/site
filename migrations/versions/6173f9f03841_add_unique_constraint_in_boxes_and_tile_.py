"""add_unique_constraint_in_boxes_and_tile_sizes

Revision ID: 6173f9f03841
Revises: 693e91c103cc
Create Date: 2025-12-03 16:14:55.107464

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6173f9f03841"
down_revision: Union[str, Sequence[str], None] = "693e91c103cc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_tile_sizes_length_width_height",
        "tile_sizes",
        ["length", "width", "height"],
    )

    op.create_unique_constraint(
        "uq_boxes_weight_area",
        "boxes",
        ["weight", "area"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_tile_sizes_length_width_height",
        "tile_sizes",
        type_="unique",
    )

    op.drop_constraint(
        "uq_boxes_weight_area",
        "boxes",
        type_="unique",
    )
