"""Add post del flag

Revision ID: 42c97d4f8366
Revises: 380e79719608
Create Date: 2025-05-15 00:40:34.229139

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "42c97d4f8366"
down_revision: Union[str, None] = "380e79719608"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "organisations",
        sa.Column(
            "vk_is_delete_prev_post",
            sa.Boolean(),
            server_default="1",
            nullable=False,
        ),
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("organisations", "vk_is_delete_prev_post")
