from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "82f83a491aea"
down_revision: Union[str, Sequence[str], None] = "0f8770cb6427"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "admins",
        sa.Column("username", sa.String(), primary_key=True),
        sa.Column("password", sa.String(), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
