"""add mode to retrievals

Revision ID: a1b2c3d4e5f6
Revises: 599ca6b25c7b
Create Date: 2026-06-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '599ca6b25c7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'retrievals',
        sa.Column('mode', sa.String(), server_default='batch', nullable=False),
    )


def downgrade() -> None:
    op.drop_column('retrievals', 'mode')
