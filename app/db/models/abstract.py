from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.db.session import Base


class Abstract(Base):
    """
    Model for persistence of titles
    """

    __tablename__ = "abstracts"

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    language: Mapped[str] = mapped_column(nullable=True, index=True)
    reference_id: Mapped[int] = mapped_column(ForeignKey("references.id"))

    reference: Mapped["app.db.models.reference.Reference"] = relationship(
        "app.db.models.reference.Reference", back_populates="abstracts", lazy="raise"
    )
