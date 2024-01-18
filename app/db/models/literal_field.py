from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class LiteralField(Base):
    """
    Model for persistence of titles
    """

    __tablename__ = "literal_fields"

    type: Mapped[str]

    __mapper_args__ = {
        "polymorphic_identity": "literal_field",
        "polymorphic_on": "type",
    }

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(nullable=False, index=True)
    language: Mapped[str] = mapped_column(nullable=True, index=True)
