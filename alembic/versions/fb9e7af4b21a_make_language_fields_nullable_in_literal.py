"""Make language fields nullable in literal

Revision ID: fb9e7af4b21a
Revises: 8ecf104af5df
Create Date: 2023-11-06 14:42:54.799916

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb9e7af4b21a'
down_revision: Union[str, None] = '8ecf104af5df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('literal_fields', 'language',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('literal_fields', 'language',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
