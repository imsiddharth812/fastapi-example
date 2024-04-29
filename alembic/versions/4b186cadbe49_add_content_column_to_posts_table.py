"""add content column to posts table

Revision ID: 4b186cadbe49
Revises: 925a1e53f798
Create Date: 2024-04-25 10:21:07.229434

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4b186cadbe49"
down_revision: Union[str, None] = "925a1e53f798"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("posts", sa.Column("content", sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column("posts", "content")
    pass
