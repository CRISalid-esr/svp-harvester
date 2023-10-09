from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.literal_field_model import LiteralField


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
    concept: Mapped["app.db.models.concept_model.Concept"] = relationship(
        "app.db.models.concept_model.Concept",
        back_populates="labels", lazy="raise")
