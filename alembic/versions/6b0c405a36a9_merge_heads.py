"""empty message

Revision ID: 6b0c405a36a9
Revises: 9e7b13a24616, bbd6b48431fe
Create Date: 2024-02-03 11:12:25.520406

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b0c405a36a9'
down_revision: Union[str, None] = ('9e7b13a24616', 'bbd6b48431fe')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
