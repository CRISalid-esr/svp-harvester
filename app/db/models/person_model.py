from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.db.models.entity_model import Entity


class Person(Entity):
    """
    Model for persisted person
    """

    __tablename__ = "people"
    id: Mapped[int] = mapped_column(ForeignKey("entities.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "person",
    }
