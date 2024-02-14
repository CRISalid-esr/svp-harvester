"""empty message

Revision ID: 54916be95355
Revises: 60268e6db772, c92b114e1074
Create Date: 2024-02-13 16:14:55.888490

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '54916be95355'
down_revision: Union[str, None] = ('60268e6db772', 'c92b114e1074')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
