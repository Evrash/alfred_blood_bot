"""change tg_id to int

Revision ID: 31945baa5ea5
Revises: 5c97b024f8ff
Create Date: 2025-03-19 23:15:16.944490

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "31945baa5ea5"
down_revision: Union[str, None] = "5c97b024f8ff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(op.f("uq_users_tg_id"), "users", ["tg_id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f("uq_users_tg_id"), "users", type_="unique")
    # ### end Alembic commands ###
