"""Create tables

Revision ID: 57941eb25b8b
Revises:
Create Date: 2025-04-09 11:06:17.513862

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "57941eb25b8b"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "organisations",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("vk_token", sa.String(), nullable=True),
        sa.Column("vk_group_id", sa.Integer(), nullable=True),
        sa.Column("vk_last_light_post", sa.String(), nullable=True),
        sa.Column("vk_is_pin_image", sa.Boolean(), nullable=False),
        sa.Column("vk_template", sa.String(), nullable=True),
        sa.Column("yd_login", sa.String(), nullable=True),
        sa.Column("yd_pass", sa.String(), nullable=True),
        sa.Column("yd_station_id", sa.String(), nullable=True),
        sa.Column("yd_groups_ids", sa.String(), nullable=True),
        sa.Column("hashtag", sa.String(), nullable=True),
        sa.Column("last_create_date", sa.DateTime(), nullable=True),
        sa.Column("last_group_state", sa.String(), nullable=True),
        sa.Column("last_image_name", sa.String(), nullable=True),
        sa.Column("last_yd_str", sa.String(), nullable=True),
        sa.Column("start_text", sa.String(), nullable=True),
        sa.Column("end_text", sa.String(), nullable=True),
        sa.Column("notification_time", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
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
    op.create_table(
        "users",
        sa.Column("tg_id", sa.String(), nullable=False),
        sa.Column("organisation_id", sa.Integer(), nullable=True),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["organisation_id"],
            ["organisations.id"],
            name=op.f("fk_users_organisation_id_organisations"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint(
            "organisation_id", name=op.f("uq_users_organisation_id")
        ),
        sa.UniqueConstraint("tg_id", name=op.f("uq_users_tg_id")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users")
    op.drop_table("organisations")
