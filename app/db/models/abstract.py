from sqlalchemy.orm import Mapped, relationship

from app.db.models.reference_literal_field import ReferenceLiteralField


class Abstract(ReferenceLiteralField):
    """
    Model for persistence of titles
    """

    __mapper_args__ = {
        "polymorphic_identity": "abstract",
    }

    reference: Mapped["app.db.models.reference.Reference"] = relationship(
        "app.db.models.reference.Reference", back_populates="abstracts", lazy="raise"
    )
