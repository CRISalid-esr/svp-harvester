from sqlalchemy.orm import Mapped, relationship

from app.db.models.reference_literal_field import ReferenceLiteralField


class Title(ReferenceLiteralField):
    """Model for persistence of titles"""

    __tablename__ = "titles"
    __mapper_args__ = {"concrete": True}
    reference: Mapped["app.db.models.reference.Reference"] = relationship(
        "app.db.models.reference.Reference", back_populates="titles", lazy="raise"
    )
