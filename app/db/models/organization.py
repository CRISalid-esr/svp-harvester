from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.affiliations import affiliations_table
from app.db.session import Base


class Organization(Base):
    """
    Model for persistence of keywords
    """

    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source: Mapped[str] = mapped_column(nullable=False, index=True)
    source_identifier: Mapped[str] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(nullable=False)

    contributions: Mapped[
        List["app.db.models.contribution.Contribution"]
    ] = relationship(
        "app.db.models.contribution.Contribution",
        secondary=affiliations_table,
        lazy="raise",
        back_populates="affiliations",
    )
