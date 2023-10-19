from typing import List

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Retrieval(Base):
    """
    Model for persistence of retrieval
    """

    __tablename__ = "retrievals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    harvestings: Mapped[List["app.db.models.harvesting.Harvesting"]] = relationship(
        "app.db.models.harvesting.Harvesting",
        back_populates="retrieval",
        cascade="all, delete",
        lazy="raise",
    )

    entity_id: Mapped[int] = mapped_column(ForeignKey("entities.id"))
    entity: Mapped["app.db.models.entity.Entity"] = relationship(
        "app.db.models.entity.Entity", back_populates="retrievals", lazy="joined"
    )

    event_types: Mapped[ARRAY[str]] = mapped_column(
        "event_types", ARRAY(String), nullable=False
    )
