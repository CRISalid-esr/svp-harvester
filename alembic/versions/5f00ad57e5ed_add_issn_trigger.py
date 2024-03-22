"""Add issn trigger

Revision ID: 5f00ad57e5ed
Revises: 7e00006b7258
Create Date: 2024-03-22 14:31:43.783307

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app.db.trigger.journal_issn_trigger import (
    CHECK_ISSN_OVERLAP,
    CREATE_TRIGGER_JOURNAL_ISSN,
    DROP_TRIGGER_JOURNAL_ISSN,
)

# revision identifiers, used by Alembic.
revision: str = "5f00ad57e5ed"
down_revision: Union[str, None] = "7e00006b7258"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(CHECK_ISSN_OVERLAP)

    # Create the trigger using the function
    op.execute(CREATE_TRIGGER_JOURNAL_ISSN)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(DROP_TRIGGER_JOURNAL_ISSN)
    # ### end Alembic commands ###
