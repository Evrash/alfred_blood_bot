"""update User, add TG ID

Revision ID: 1a43900668e6
Revises: 7c8e87d6a1b5
Create Date: 2025-03-19 03:32:42.364316

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1a43900668e6"
down_revision: Union[str, None] = "7c8e87d6a1b5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("tg_id", sa.String(), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "tg_id")
