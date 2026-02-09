from enum import Enum

from app.db.session import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates


class ReferenceIdentifier(Base):
    """
    Model for persistence of reference identifiers
    """

    class IdentifierType(Enum):
        """Enum for reference identifier types (application-level validation only)."""

        DOI = "doi"
        HAL = "hal"
        PMID = "pmid"
        OPENALEX = "openalex"
        NNT = "nnt"
        PPN = "ppn"
        URI = "uri"
        ARXIV = "arxiv"
        BIBCODE = "bibcode"
        BIORXIV = "biorxiv"
        CERN = "cern"
        CHEMRXIV = "chemrxiv"
        ENSAM = "ensam"
        INERIS = "ineris"
        INSPIRE = "inspire"
        IRD = "ird"
        IRSTEA = "irstea"
        IRTHESAURUS = "irthesaurus"
        MEDITAGRI = "meditagri"
        OKINA = "okina"
        OATAO = "oatao"
        PII = "pii"
        PRODINRA = "prodinra"
        PUBMEDCENTRAL = "pubmedcentral"
        SCIENCESPO = "sciencespo"
        SWHID = "swhid"
        WOS = "wos"

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

        if id_type == ReferenceIdentifier.IdentifierType.DOI.value:
            low = v.lower()
            for prefix in ("urn:doi:", "https://doi.org/"):
                if low.startswith(prefix):
                    v = v[len(prefix) :]
                    break

        if id_type == ReferenceIdentifier.IdentifierType.NNT.value:
            v = v.upper()

        # sudoc ppn may contain a trailing 'X' which case can vary among sources
        if id_type == ReferenceIdentifier.IdentifierType.PPN.value:
            v = v.upper()

        return v

    @validates("type", include_removes=False, include_backrefs=True)
    def _validate_type(self, _, new_type: str):
        """
        1) Validate type is among supported enum values
        2) If type changes and value already exists, re-normalize the value accordingly
        """
        if new_type not in [t.value for t in self.IdentifierType]:
            raise ValueError(f"Identifier type {new_type} is not supported")

        current_value = getattr(self, "value", None)
        if current_value is not None:
            self.value = self._normalize_value(new_type, current_value)

        return new_type

    @validates("value")
    def _validate_value(self, _, raw_value: str | None):
        return self._normalize_value(getattr(self, "type", None), raw_value)
