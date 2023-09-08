from typing import List

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Retrieval(Base):
    __tablename__ = "retrievals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    harvesters: Mapped[List["Harvesting"]] = relationship(
        back_populates="retrieval", cascade="all, delete"
    )

    entity_id: Mapped[int] = mapped_column(ForeignKey("entities.id"))
    entity: Mapped["Entity"] = relationship(back_populates="retrievals")


class Harvesting(Base):
    __tablename__ = "harvestings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    harvester = Column(String, index=True)
    retrieval_id: Mapped[int] = mapped_column(ForeignKey("retrievals.id"))
    retrieval: Mapped["Retrieval"] = relationship(back_populates="harvesters")


class Entity(Base):
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

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name!r})"


class Identifier(Base):
    __tablename__ = "identifiers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type = Column(String, index=True)
    entity_id: Mapped[int] = mapped_column(ForeignKey("entities.id"))
    entity: Mapped["Entity"] = relationship(back_populates="identifiers")


class Person(Entity):
    __tablename__ = "people"
    id: Mapped[int] = mapped_column(ForeignKey("entities.id"), primary_key=True)
    last_name: Mapped[str]
    first_name: Mapped[str]

    __mapper_args__ = {
        "polymorphic_identity": "person",
    }
