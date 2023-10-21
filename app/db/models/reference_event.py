from enum import Enum

from sqlalchemy import ForeignKey, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ReferenceEvent(Base):
    """
    Model for persistence of events related to references
    """

    __tablename__ = "reference_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type: Mapped[str] = mapped_column(nullable=False, index=True)

    reference_id: Mapped[int] = mapped_column(ForeignKey("references.id"))
    reference: Mapped["app.db.models.reference.Reference"] = relationship(
        "app.db.models.reference.Reference",
        back_populates="reference_events",
        lazy="joined",
    )

    harvesting_id: Mapped[int] = mapped_column(ForeignKey("harvestings.id"))
    harvesting: Mapped["app.db.models.harvesting.Harvesting"] = relationship(
        "app.db.models.harvesting.Harvesting",
        back_populates="reference_events",
        lazy="joined",
    )

    # boolean field "history"
    history: Mapped[bool] = mapped_column(nullable=False, index=True, default=True)

    class Type(Enum):
        """Reference events types"""

        CREATED = "created"
        UPDATED = "updated"
        DELETED = "deleted"
        UNCHANGED = "unchanged"


@event.listens_for(ReferenceEvent, "before_insert")
def receive_before_insert(_, __, target):
    """Set the reference deleted flag to True if the event type is deleted"""
    if target.type == ReferenceEvent.Type.DELETED.value and target.history:
        target.reference.deleted = True
