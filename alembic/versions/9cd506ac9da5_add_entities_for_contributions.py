"""Add entities for contributions

Revision ID: 9cd506ac9da5
Revises: fb9e7af4b21a
Create Date: 2023-11-16 09:30:40.410915

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9cd506ac9da5'
down_revision: Union[str, None] = 'fb9e7af4b21a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contributors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('source', sa.String(), nullable=False),
    sa.Column('source_identifier', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contributors_id'), 'contributors', ['id'], unique=False)
    op.create_index(op.f('ix_contributors_source'), 'contributors', ['source'], unique=False)
    op.create_index(op.f('ix_contributors_source_identifier'), 'contributors', ['source_identifier'], unique=False)
    op.create_table('contributions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rank', sa.Integer(), nullable=True),
    sa.Column('contributor_id', sa.Integer(), nullable=False),
    sa.Column('reference_id', sa.Integer(), nullable=False),
    sa.Column('role', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['contributor_id'], ['contributors.id'], ),
    sa.ForeignKeyConstraint(['reference_id'], ['references.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contributions_id'), 'contributions', ['id'], unique=False)
    op.create_index(op.f('ix_contributions_role'), 'contributions', ['role'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_contributions_role'), table_name='contributions')
    op.drop_index(op.f('ix_contributions_id'), table_name='contributions')
    op.drop_table('contributions')
    op.drop_index(op.f('ix_contributors_source_identifier'), table_name='contributors')
    op.drop_index(op.f('ix_contributors_source'), table_name='contributors')
    op.drop_index(op.f('ix_contributors_id'), table_name='contributors')
    op.drop_table('contributors')
    # ### end Alembic commands ###