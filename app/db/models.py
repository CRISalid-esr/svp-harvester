from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List

from dataclasses_json import dataclass_json
from sqlalchemy import Column, String, ForeignKey, DateTime, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.identifiers import IdentifierTypeEnum


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
    harvesting: Mapped[List["Harvesting"]] = relationship(
        back_populates="retrieval", cascade="all, delete"
    )

    entity_id: Mapped[int] = mapped_column(ForeignKey("entities.id"))
    entity: Mapped["Entity"] = relationship(back_populates="retrievals", lazy="joined")


@dataclass_json
@dataclass
class Harvesting(Base):
    """Model for persistence of harvestings"""

    __tablename__ = "harvestings"

    # pylint: disable=C0103
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    harvester: Mapped[str] = mapped_column(nullable=False, index=True)
    retrieval_id: Mapped[int] = mapped_column(ForeignKey("retrievals.id"))
    retrieval: Mapped["Retrieval"] = relationship(
        back_populates="harvesting", lazy="raise"
    )

    state: Mapped[str] = mapped_column(
        nullable=False, index=True, default=State.IDLE.value
    )

    reference_events: Mapped[List["ReferenceEvent"]] = relationship(
        back_populates="harvesting", cascade="all, delete"
    )

    timestamp: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)


class Identifier(Base):
    """
    Model for persistence of identifiers
    """

    __tablename__ = "identifiers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type: Mapped[str] = mapped_column(nullable=False, index=True)
    value: Mapped[str] = mapped_column(nullable=False, index=True)
    entity_id: Mapped[int] = mapped_column(ForeignKey("entities.id"))
    entity: Mapped["Entity"] = relationship(back_populates="identifiers", lazy="raise")

    class Type(Enum):
        """Identifier types"""

        ORCID = "orcid"
        IDREF = "idref"
        ID_HAL_I = "id_hal_i"
        ID_HAL_S = "id_hal_s"


class Entity(Base):
    """
    Base Model for entities for which we want to fetch references
    """

    __tablename__ = "entities"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str]

    __mapper_args__ = {
        "polymorphic_identity": "entity",
        "polymorphic_on": "type",
    }

    identifiers: Mapped[List["Identifier"]] = relationship(
        back_populates="entity", cascade="all, delete", lazy="joined"
    )

    retrievals: Mapped[List["Retrieval"]] = relationship(
        back_populates="entity", cascade="all, delete", lazy="raise"
    )

    def get_identifier(self, identifier_type: IdentifierTypeEnum) -> str | None:
        """
        Get identifier value for a given type

        :param identifier_type: type of the identifier
        :return: the identifier or None if not found
        """
        for identifier in self.identifiers:
            if identifier.type == identifier_type.value:
                return identifier.value
        return None


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


references_subjects_table = Table(
    "references_subjects_table",
    Base.metadata,
    Column("reference_id", ForeignKey("references.id")),
    Column("concept_id", ForeignKey("concepts.id")),
)


class LiteralField(Base):
    """
    Model for persistence of titles
    """

    __tablename__ = "literal_fields"

    type: Mapped[str]

    __mapper_args__ = {
        "polymorphic_identity": "literal_field",
        "polymorphic_on": "type",
    }

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    value: Mapped[str] = mapped_column(nullable=False)
    language: Mapped[str] = mapped_column(nullable=False, index=True)


class Title(LiteralField):
    """
    Model for persistence of titles
    """

    __tablename__ = "titles"

    id: Mapped[int] = mapped_column(ForeignKey("literal_fields.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "title",
    }

    reference_id: Mapped[int] = mapped_column(ForeignKey("references.id"))
    reference: Mapped["Reference"] = relationship(back_populates="titles", lazy="raise")


class Subtitle(LiteralField):
    """
    Model for persistence of subtitles
    """

    __tablename__ = "subtitles"

    id: Mapped[int] = mapped_column(ForeignKey("literal_fields.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "subtitle",
    }

    reference_id: Mapped[int] = mapped_column(ForeignKey("references.id"))
    reference: Mapped["Reference"] = relationship(
        back_populates="subtitles", lazy="raise"
    )


class Label(LiteralField):
    """
    Model for persistence of keyword labels
    """

    __tablename__ = "labels"

    id: Mapped[int] = mapped_column(ForeignKey("literal_fields.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "label",
    }

    concept_id: Mapped[int] = mapped_column(ForeignKey("concepts.id"))
    concept: Mapped["Concept"] = relationship(back_populates="labels", lazy="raise")


class Concept(Base):
    """
    Model for persistence of keywords
    """

    __tablename__ = "concepts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    uri: Mapped[str] = mapped_column(nullable=True, index=False, unique=True)

    labels: Mapped[List["Label"]] = relationship(
        back_populates="concept", cascade="all, delete", lazy="joined"
    )


class Reference(Base):
    """
    Model for persistence of references
    """

    __tablename__ = "references"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_identifier: Mapped[str] = mapped_column(nullable=False, index=True)
    titles: Mapped[List["Title"]] = relationship(
        back_populates="reference", cascade="all, delete", lazy="joined"
    )
    subtitles: Mapped[List["Subtitle"]] = relationship(
        back_populates="reference", cascade="all, delete", lazy="joined"
    )

    subjects: Mapped[List[Concept]] = relationship(secondary=references_subjects_table)

    reference_events: Mapped[List["ReferenceEvent"]] = relationship(
        back_populates="reference", cascade="all, delete", lazy="raise"
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
    reference: Mapped["Reference"] = relationship(
        back_populates="reference_events", lazy="joined"
    )

    harvesting_id: Mapped[int] = mapped_column(ForeignKey("harvestings.id"))
    harvesting: Mapped["Harvesting"] = relationship(
        back_populates="reference_events", lazy="joined"
    )

    class Type(Enum):
        """Reference events types"""

        CREATED = "created"
        UPDATED = "updated"
        DELETED = "deleted"
        UNCHANGED = "unchanged"
