from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.literal_field_model import LiteralField


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
    reference: Mapped["app.db.models.reference_model.Reference"] = relationship(
        "app.db.models.reference_model.Reference",
        back_populates="subtitles", lazy="raise"
    )
