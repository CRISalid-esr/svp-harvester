"""empty message

Revision ID: c18a66148821
Revises: d711b3228446, f6a84408b053
Create Date: 2024-01-18 11:42:15.020723

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c18a66148821"
down_revision: Union[str, None] = ("d711b3228446", "f6a84408b053")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
