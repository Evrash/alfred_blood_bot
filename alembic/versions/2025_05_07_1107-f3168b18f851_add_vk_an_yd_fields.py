"""add vk an yd fields

Revision ID: f3168b18f851
Revises: 57941eb25b8b
Create Date: 2025-05-07 11:07:24.927546

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f3168b18f851"
down_revision: Union[str, None] = "57941eb25b8b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "organisations",
        sa.Column("vk_last_pub_date", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "organisations",
        sa.Column("vk_last_post_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "organisations",
        sa.Column("yd_last_pub_date", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("organisations", "yd_last_pub_date")
    op.drop_column("organisations", "vk_last_post_id")
    op.drop_column("organisations", "vk_last_pub_date")
