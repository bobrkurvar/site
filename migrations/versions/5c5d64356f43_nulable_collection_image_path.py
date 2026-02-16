"""nulable_collection_image_path

Revision ID: 5c5d64356f43
Revises: 564659581c45
Create Date: 2026-02-15 18:43:07.566893

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5c5d64356f43"
down_revision: Union[str, Sequence[str], None] = "564659581c45"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("collections", "image_path", nullable=True)
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
