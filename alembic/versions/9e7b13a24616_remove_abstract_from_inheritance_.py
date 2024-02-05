"""Remove abstract from inheritance hierarchy and convert value to text type

Revision ID: 9e7b13a24616
Revises: 352109cd8dd5
Create Date: 2024-01-31 10:23:56.805381

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9e7b13a24616"
down_revision: Union[str, None] = "352109cd8dd5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "abstracts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("language", sa.String(), nullable=True),
        sa.Column("reference_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["reference_id"],
            ["references.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_abstracts_language"), "abstracts", ["language"], unique=False
    )
    op.create_index(op.f("ix_abstracts_value"), "abstracts", ["value"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_abstracts_value"), table_name="abstracts")
    op.drop_index(op.f("ix_abstracts_language"), table_name="abstracts")
    op.drop_table("abstracts")
    # ### end Alembic commands ###
