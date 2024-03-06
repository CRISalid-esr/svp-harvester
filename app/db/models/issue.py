from typing import List

from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Issue(Base):
    """
    Model for persistence of journal issues
    """

    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(nullable=False, index=True)
    source_identifier: Mapped[str] = mapped_column(nullable=False, index=True)

    volume: Mapped[str] = mapped_column(nullable=True, index=True)
    number: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False, default=[])

    rights: Mapped[str] = mapped_column(nullable=True, index=False)
    date: Mapped[str] = mapped_column(nullable=True, index=True)

    references: Mapped[List["app.db.models.reference.Reference"]] = relationship(
        "app.db.models.reference.Reference",
        back_populates="issue",
        lazy="raise",
    )

    journal_id: Mapped[int] = mapped_column(ForeignKey("journals.id"))
    journal: Mapped["app.db.models.journal.Journal"] = relationship(
        "app.db.models.journal.Journal", back_populates="issues", lazy="raise"
    )
