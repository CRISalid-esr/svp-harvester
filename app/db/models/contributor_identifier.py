import re
from enum import Enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, validates, relationship

from app.db.session import Base


class ContributorIdentifier(Base):
    """
    Model for persistence of identifiers
    """

    class IdentifierType(Enum):
        """Enum for identifier types"""

        # --PERSON IDENTIFIERS--
        ORCID = "orcid"
        OPEN_ALEX = "openalex"
        IDHAL_I = "idhali"
        IDHAL_S = "idhals"
        IDREF = "idref"
        SCOPUS = "scopus"
        GOOGLE_SCHOLAR = "googlescholar"
        VIAF = "viaf"
        ISNI = "isni"
        RESEARCHER_ID = "researcherid"

    __tablename__ = "contributor_identifier"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(nullable=False, index=True)
    value: Mapped[str] = mapped_column(nullable=False, index=True)
    source: Mapped[str] = mapped_column(nullable=False, index=True)

    contributor_id: Mapped[int] = mapped_column(
        ForeignKey("contributors.id"), nullable=False, index=True
    )
    contributor: Mapped["app.db.models.contributor.Contributor"] = relationship(
        "app.db.models.contributor.Contributor",
        back_populates="identifiers",
        lazy="joined",
    )

    _NORMALIZATION_REGEX = {
        IdentifierType.ORCID.value: re.compile(r"^https?://orcid.org/"),
        IdentifierType.OPEN_ALEX.value: re.compile(r"^https?://openalex.org/"),
        # Match start of URL + strip domain, and also drop a trailing '/id' if present
        IdentifierType.IDREF.value: re.compile(r"^https?://(?:www\.)?idref\.fr/|/id$"),
        IdentifierType.ISNI.value: re.compile(r"^https?://isni.org/isni/"),
        IdentifierType.VIAF.value: re.compile(r"^https?://viaf.org/viaf/"),
        IdentifierType.GOOGLE_SCHOLAR.value: re.compile(
            r"^https?://scholar.google.[^/]+/citations\?user="
        ),
        # IDHAL and SCOPUS usually already stored as bare identifiers
    }

    @validates("type", include_removes=False, include_backrefs=True)
    def _valid_identifier_is_among_supported_types(self, _, new_type):
        """
        Validate that the identifier is among the supported types
        """
        if new_type not in [identifier.value for identifier in self.IdentifierType]:
            raise ValueError(f"Identifier type {new_type} is not supported")
        return new_type

    @validates("value")
    def _normalize_identifier_value(self, _, new_value: str):
        """
        Normalize identifier value by removing URL prefixes depending on type.
        """
        regex = self._NORMALIZATION_REGEX.get(self.type)
        if regex:
            new_value = regex.sub("", new_value)
        return new_value
