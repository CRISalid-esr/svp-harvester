from sqlalchemy.orm import Mapped, relationship

from app.db.models.reference_literal_field import ReferenceLiteralField


class Subtitle(ReferenceLiteralField):
    """Model for persistence of subtitles"""

    __tablename__ = "subtitles"
    __mapper_args__ = {"concrete": True}

    reference: Mapped["app.db.models.reference.Reference"] = relationship(
        "app.db.models.reference.Reference", back_populates="subtitles", lazy="raise"
    )
