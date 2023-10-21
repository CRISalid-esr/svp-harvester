"""Add deleted fields to references

Revision ID: fea6e3782e16
Revises: 472729c5be0e
Create Date: 2023-10-21 10:13:41.933168

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fea6e3782e16'
down_revision: Union[str, None] = '472729c5be0e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('references', sa.Column('deleted', sa.Boolean(), nullable=False))
    op.create_index(op.f('ix_references_deleted'), 'references', ['deleted'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_references_deleted'), table_name='references')
    op.drop_column('references', 'deleted')
    # ### end Alembic commands ###
