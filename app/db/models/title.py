from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.literal_field import LiteralField


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
    reference: Mapped["app.db.models.reference.Reference"] = relationship(
        "app.db.models.reference.Reference",
        back_populates="titles", lazy="raise")
