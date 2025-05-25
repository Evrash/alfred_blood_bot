"""stat

Revision ID: c5ed9e49fa13
Revises: 42c97d4f8366
Create Date: 2025-05-23 19:52:36.285526

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c5ed9e49fa13"
down_revision: Union[str, None] = "42c97d4f8366"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "statistic",
        sa.PrimaryKeyConstraint("id", name=op.f("pk_statistic")),
        sa.Column("organisation_id", sa.Integer(), nullable=True),
        sa.Column(
            "o_plus",
            sa.Enum("red", "yellow", "green", name="bloodcolor"),
            nullable=False,
        ),
        sa.Column(
            "o_minus",
            sa.Enum("red", "yellow", "green", name="bloodcolor"),
            nullable=False,
        ),
        sa.Column(
            "a_plus",
            sa.Enum("red", "yellow", "green", name="bloodcolor"),
            nullable=False,
        ),
        sa.Column(
            "a_minus",
            sa.Enum("red", "yellow", "green", name="bloodcolor"),
            nullable=False,
        ),
        sa.Column(
            "b_plus",
            sa.Enum("red", "yellow", "green", name="bloodcolor"),
            nullable=False,
        ),
        sa.Column(
            "b_minus",
            sa.Enum("red", "yellow", "green", name="bloodcolor"),
            nullable=False,
        ),
        sa.Column(
            "ab_plus",
            sa.Enum("red", "yellow", "green", name="bloodcolor"),
            nullable=False,
        ),
        sa.Column(
            "ab_minus",
            sa.Enum("red", "yellow", "green", name="bloodcolor"),
            nullable=False,
        ),
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
            name=op.f("fk_statistic_organisation_id_organisations"),
        ),

    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("statistic")