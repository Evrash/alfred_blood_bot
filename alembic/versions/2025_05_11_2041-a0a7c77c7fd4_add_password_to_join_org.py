"""Add password to join org

Revision ID: a0a7c77c7fd4
Revises: f3168b18f851
Create Date: 2025-05-11 20:41:01.720942

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a0a7c77c7fd4"
down_revision: Union[str, None] = "f3168b18f851"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "organisations", sa.Column("join_password", sa.String(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("organisations", "join_password")
