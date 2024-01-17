from typing import List

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Contributor(Base):
    """
    Model for persistence of contributors
    """

    __tablename__ = "contributors"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source: Mapped[str] = mapped_column(nullable=False, index=True)
    source_identifier: Mapped[str] = mapped_column(nullable=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False, index=True)

    contributions: Mapped[
        List["app.db.models.contribution.Contribution"]
    ] = relationship(
        "app.db.models.contribution.Contribution",
        back_populates="contributor",
        cascade="all, delete-orphan",
        lazy="raise",
    )

    # use postgresql array type
    name_variants: Mapped[List[str]] = mapped_column(
        ARRAY(String), nullable=False, default=[]
    )
