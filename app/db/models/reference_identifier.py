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
    value: Mapped[str] = mapped_column("value", nullable=False, index=True)

    reference: Mapped["app.db.models.reference.Reference"] = relationship(
        "app.db.models.reference.Reference", back_populates="identifiers", lazy="raise"
    )
    reference_id: Mapped[int] = mapped_column(ForeignKey("references.id"), index=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._normalize()

    @staticmethod
    def _normalize_value(id_type: str | None, raw_value: str | None) -> str | None:
        if raw_value is None:
            return None

        # universal normalization
        v = raw_value.strip()

        if not id_type:
            return v

        if id_type == "doi":
            low = v.lower()
            for prefix in ("urn:doi:", "https://doi.org/"):
                if low.startswith(prefix):
                    v = v[len(prefix) :]
                    break

        if id_type == "nnt":
            v = v.upper()

        return v

    def _normalize(self) -> None:
        """
        Normalize current stored value if we have at least a value
        """
        current_type = self.__dict__.get("type")
        current_value = self.__dict__.get("value")
        normalized = self._normalize_value(current_type, current_value)
        if normalized is not None and normalized != current_value:
            self.__dict__["value"] = normalized

    @property
    def value(self) -> str:
        """
        Get the value of the identifier.
        """
        return self.__dict__.get("value")

    @value.setter
    def value(self, raw_value: str) -> None:
        """
        Set the value (may run before type is set).
        We normalize with whatever type we currently have (possibly None),
        and we will normalize again when type is later assigned.
        """
        current_type = self.__dict__.get("type")
        self.__dict__["value"] = self._normalize_value(current_type, raw_value)

    @property
    def type(self) -> str:
        return self.__dict__.get("type")

    @type.setter
    def type(self, raw_type: str) -> None:
        """
        Set the type, then normalize the already-stored value accordingly.
        This handles the case where value was set before type.
        """
        self.__dict__["type"] = raw_type
        self._normalize()
