"""empty message

Revision ID: 60268e6db772
Revises: 6d0387871d88, a60cf7db9469
Create Date: 2024-02-07 17:24:23.507792

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '60268e6db772'
down_revision: Union[str, None] = ('6d0387871d88', 'a60cf7db9469')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
