from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class ReferenceIdentifier(Base):
    """
    Model for persistence of reference identifiers
    """

    __tablename__ = "reference_identifiers"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(nullable=False, index=True)
    _value: Mapped[str] = mapped_column("value", nullable=False, index=True)

    reference: Mapped["app.db.models.reference.Reference"] = relationship(
        "app.db.models.reference.Reference", back_populates="identifiers", lazy="raise"
    )
    reference_id: Mapped[int] = mapped_column(ForeignKey("references.id"), index=True)

    @property
    def value(self) -> str:
        """
        Get the value of the identifier.
        :return: The value of the identifier.
        """
        return self._value

    @value.setter
    def value(self, raw_value: str) -> None:
        """
        Set the value of the identifier.
        :param raw_value: The raw value to set.
        :return: None
        """
        if self.type == "doi":
            for prefix in ("urn:doi:", "https://doi.org/"):
                if raw_value.startswith(prefix):
                    raw_value = raw_value[len(prefix) :]
                    break
        self._value = raw_value
