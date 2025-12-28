# pylint: disable=duplicate-code
import re
from enum import Enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column, validates

from app.db.session import Base


class OrganizationIdentifier(Base):
    """
    Model for persistence of organization identifiers
    """

    class IdentifierType(Enum):
        """Enum for identifier types"""

        OPEN_ALEX = "open_alex"
        HAL = "hal"
        IDREF = "idref"
        VIAF = "viaf"
        ISNI = "isni"
        ROR = "ror"
        SCOPUS = "scopus"
        RNSR = "nns"

    __tablename__ = "organization_identifiers"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(nullable=False, index=True)
    value: Mapped[str] = mapped_column(nullable=False, index=True)

    organization: Mapped["app.db.models.organization.Organization"] = relationship(
        "app.db.models.organization.Organization",
        back_populates="identifiers",
        lazy="raise",
    )
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), index=True
    )

    _NORMALIZATION_REGEX = {
        IdentifierType.OPEN_ALEX.value: re.compile(r"^https?://openalex.org/"),
        # Match start of URL + strip domain, and also drop a trailing '/id' if present
        IdentifierType.IDREF.value: re.compile(r"^https?://(?:www\.)?idref\.fr/|/id$"),
        IdentifierType.ISNI.value: re.compile(r"^https?://isni.org/isni/"),
        IdentifierType.VIAF.value: re.compile(r"^https?://viaf.org/viaf/"),
        IdentifierType.ROR.value: re.compile(r"^https?://ror.org/"),
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
