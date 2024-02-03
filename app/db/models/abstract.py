from sqlalchemy import Text
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.db.models.reference_literal_field import ReferenceLiteralField


class Abstract(ReferenceLiteralField):
    """Model for persistence of abstracts"""

    __tablename__ = "abstracts"
    __mapper_args__ = {"concrete": True}

    value: Mapped[str] = mapped_column(Text, nullable=False, index=False)
    reference = relationship("Reference", back_populates="abstracts", lazy="raise")
