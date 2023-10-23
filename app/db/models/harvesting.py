from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List

from dataclasses_json import dataclass_json
from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


@dataclass_json
@dataclass
class Harvesting(Base):
    """Model for persistence of harvestings"""

    __tablename__ = "harvestings"

    class State(Enum):
        """Identifier types"""

        IDLE = "idle"
        RUNNING = "running"
        COMPLETED = "completed"
        FAILED = "failed"

    # pylint: disable=C0103
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    harvester: Mapped[str] = mapped_column(nullable=False, index=True)
    retrieval_id: Mapped[int] = mapped_column(ForeignKey("retrievals.id"))
    retrieval: Mapped["app.db.models.retrieval.Retrieval"] = relationship(
        "app.db.models.retrieval.Retrieval", back_populates="harvestings", lazy="raise"
    )

    state: Mapped[str] = mapped_column(
        nullable=False, index=True, default=State.IDLE.value
    )

    reference_events: Mapped[
        List["app.db.models.reference_event.ReferenceEvent"]
    ] = relationship(
        "app.db.models.reference_event.ReferenceEvent",
        back_populates="harvesting",
        cascade="all, delete",
        lazy="joined",
    )

    # boolean field "history"
    history: Mapped[bool] = mapped_column(nullable=False, index=True, default=True)

    timestamp: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
