from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ReferenceLiteralField(Base):
    """
    Model for persistence of titles
    """

    __tablename__ = "reference_literal_fields"

    type: Mapped[str]

    __mapper_args__ = {
        "polymorphic_identity": "reference_literal_field",
        "polymorphic_on": "type",
    }

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(nullable=False, index=True)
    language: Mapped[str] = mapped_column(nullable=True, index=True)

    reference_id: Mapped[int] = mapped_column(ForeignKey("references.id"))
