from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List

from dataclasses_json import dataclass_json
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class State(Enum):
    """Identifier types"""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Retrieval(Base):
    """
    Model for persistence of retrieval
    """

    __tablename__ = "retrievals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    harvesters: Mapped[List["Harvesting"]] = relationship(
        back_populates="retrieval", cascade="all, delete"
    )

    entity_id: Mapped[int] = mapped_column(ForeignKey("entities.id"))
    entity: Mapped["Entity"] = relationship(back_populates="retrievals")


@dataclass_json
@dataclass
class Harvesting(Base):
    """Model for persistence of harvestings"""

    __tablename__ = "harvestings"

    # pylint: disable=C0103
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    harvester: Mapped[str] = mapped_column(nullable=False, index=True)
    retrieval_id: Mapped[int] = mapped_column(ForeignKey("retrievals.id"))
    retrieval: Mapped["Retrieval"] = relationship(back_populates="harvesters")

    state: Mapped[str] = mapped_column(
        nullable=False, index=True, default=State.IDLE.value
    )

    reference_events: Mapped[List["ReferenceEvent"]] = relationship(
        back_populates="harvesting", cascade="all, delete"
    )

    timestamp: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)


class Entity(Base):
    """
    Base Model for entities for which we want to fetch references
    """

    __tablename__ = "entities"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str]

    __mapper_args__ = {
        "polymorphic_identity": "employee",
        "polymorphic_on": "type",
    }

    identifiers: Mapped[List["Identifier"]] = relationship(
        back_populates="entity", cascade="all, delete"
    )

    retrievals: Mapped[List["Retrieval"]] = relationship(
        back_populates="entity", cascade="all, delete"
    )


class Identifier(Base):
    """
    Model for persistence of identifiers
    """

    __tablename__ = "identifiers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type: Mapped[str] = mapped_column(nullable=False, index=True)
    value: Mapped[str] = mapped_column(nullable=False, index=True)
    entity_id: Mapped[int] = mapped_column(ForeignKey("entities.id"))
    entity: Mapped["Entity"] = relationship(back_populates="identifiers")


class Person(Entity):
    """
    Model for persisted person
    """

    __tablename__ = "people"
    id: Mapped[int] = mapped_column(ForeignKey("entities.id"), primary_key=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    first_name: Mapped[str] = mapped_column(nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "person",
    }


class Reference(Base):
    """
    Model for persistence of references
    """

    __tablename__ = "references"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_identifier: Mapped[str] = mapped_column(nullable=False, index=True)
    title: Mapped[str]

    reference_events: Mapped[List["ReferenceEvent"]] = relationship(
        back_populates="reference", cascade="all, delete"
    )

    hash: Mapped[str] = mapped_column(String, index=True)


class ReferenceEvent(Base):
    """
    Model for persistence of events related to references
    """

    __tablename__ = "reference_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type: Mapped[str] = mapped_column(nullable=False, index=True)

    reference_id: Mapped[int] = mapped_column(ForeignKey("references.id"))
    reference: Mapped["Reference"] = relationship(back_populates="reference_events")

    harvesting_id: Mapped[int] = mapped_column(ForeignKey("harvestings.id"))
    harvesting: Mapped["Harvesting"] = relationship(back_populates="reference_events")
