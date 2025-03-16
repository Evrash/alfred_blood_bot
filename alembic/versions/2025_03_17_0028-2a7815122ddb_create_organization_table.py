"""create organization table

Revision ID: 2a7815122ddb
Revises:
Create Date: 2025-03-17 00:28:20.594280

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2a7815122ddb"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "organisations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("vk_token", sa.String(), nullable=True),
        sa.Column("vk_group_id", sa.Integer(), nullable=True),
        sa.Column("vk_last_light_post", sa.String(), nullable=True),
        sa.Column("vk_is_pin_image", sa.Boolean(), nullable=False),
        sa.Column("vk_template", sa.Integer(), nullable=True),
        sa.Column("yd_login", sa.String(), nullable=True),
        sa.Column("yd_pass", sa.String(), nullable=True),
        sa.Column("yd_station_id", sa.String(), nullable=True),
        sa.Column("yd_groups_ids", sa.String(), nullable=True),
        sa.Column("hashtag", sa.String(), nullable=True),
        sa.Column("last_create_date", sa.DateTime(), nullable=True),
        sa.Column("last_group_state", sa.String(), nullable=True),
        sa.Column("start_text", sa.String(), nullable=True),
        sa.Column("end_text", sa.String(), nullable=True),
        sa.Column("notification_time", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_organisations")),
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("organisations")
