from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.db.models.entity_model import Entity


class Person(Entity):
    """
    Model for persisted person
    """

    __tablename__ = "people"
    id: Mapped[int] = mapped_column(ForeignKey("entities.id"), primary_key=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    first_name: Mapped[str] = mapped_column(nullable=True)
    full_name: Mapped[str] = mapped_column(nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "person",
    }

    @validates('first_name', 'last_name')
    def update_full_name(self, attribute_name, new_value):
        """ Temp"""
        if attribute_name == "first_name":
            self.full_name = f"{new_value} {self.last_name or ''}".strip()
        else:
            self.full_name = f"{self.first_name or ''} {new_value}".strip()
        return new_value
