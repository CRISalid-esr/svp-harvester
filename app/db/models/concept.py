import datetime
from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Concept(Base):
    """
    Model for persistence of keywords
    """

    __tablename__ = "concepts"

    id: Mapped[int] = mapped_column(primary_key=True)

    uri: Mapped[str] = mapped_column(nullable=True, index=True, unique=True)

    labels: Mapped[List["app.db.models.label.Label"]] = relationship(
        "app.db.models.label.Label",
        back_populates="concept",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    dereferenced: Mapped[bool] = mapped_column(nullable=False, default=False)
    # timestamp of last successful dereferencing
    last_dereferencing_date_time: Mapped[datetime.datetime] = mapped_column(
        nullable=True, default=None
    )
