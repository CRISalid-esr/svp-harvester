from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Retrieval(Base):
    """
    Model for persistence of retrieval
    """

    __tablename__ = "retrievals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    harvestings: Mapped[List["app.db.models.harvesting_model.Harvesting"]] = relationship(
        "app.db.models.harvesting_model.Harvesting",
        back_populates="retrieval", cascade="all, delete", lazy="raise"
    )

    entity_id: Mapped[int] = mapped_column(ForeignKey("entities.id"))
    entity: Mapped["app.db.models.entity_model.Entity"] = relationship(
        "app.db.models.entity_model.Entity",
        back_populates="retrievals", lazy="joined")
