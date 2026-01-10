from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from app.db.session import Base


class ReferenceIdentifier(Base):
    """
    Model for persistence of reference identifiers
    """

    __tablename__ = "reference_identifiers"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(nullable=False, index=True)
    value: Mapped[str] = mapped_column(nullable=False, index=True)

    reference: Mapped["app.db.models.reference.Reference"] = relationship(
        "app.db.models.reference.Reference", back_populates="identifiers", lazy="raise"
    )
    reference_id: Mapped[int] = mapped_column(ForeignKey("references.id"), index=True)

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

    @validates("value")
    def _validate_value(self, _, raw_value):
        return self._normalize_value(getattr(self, "type", None), raw_value)

    @validates("type")
    def _validate_type(self, _, raw_type):
        # When type changes, re-normalize the value
        current_value = getattr(self, "value", None)
        if current_value is not None:
            self.value = self._normalize_value(raw_type, current_value)
        return raw_type
