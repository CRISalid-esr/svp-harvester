"""Add addition_files field to manifestation model

Revision ID: 808af9258e7f
Revises: 7161ca0b88de
Create Date: 2024-06-13 09:26:39.916027

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '808af9258e7f'
down_revision: Union[str, None] = '7161ca0b88de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reference_manifestations', sa.Column('additional_files', postgresql.ARRAY(sa.String()), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('reference_manifestations', 'additional_files')
    # ### end Alembic commands ###
