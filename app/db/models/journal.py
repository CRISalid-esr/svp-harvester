from typing import List

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Journal(Base):
    """
    Model for persistence of journals
    """

    __tablename__ = "journals"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(nullable=False, index=True)
    source_identifier: Mapped[str] = mapped_column(nullable=False, index=True)

    issn: Mapped[str] = mapped_column(nullable=True, index=True)
    eissn: Mapped[str] = mapped_column(nullable=True, index=True)
    publisher: Mapped[str] = mapped_column(nullable=True, index=False)

    titles: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False, default=[])

    issues: Mapped[List["app.db.models.issue.Issue"]] = relationship(
        "app.db.models.issue.Issue",
        back_populates="journal",
        cascade="all, delete",
        lazy="raise",
    )
