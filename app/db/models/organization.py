from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.affiliations import affiliations_table
from app.db.models.organization_identifier import (  # pylint: disable=unused-import
    OrganizationIdentifier,
)
from app.db.session import Base


class Organization(Base):
    """
    Model for persistence of keywords
    """

    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(nullable=False, index=True)
    source_identifier: Mapped[str] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=True, index=True)
    identifiers: Mapped[
        List["app.db.models.organization_identifier.OrganizationIdentifier"]
    ] = relationship(
        "app.db.models.organization_identifier.OrganizationIdentifier",
        back_populates="organization",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    contributions: Mapped[
        List["app.db.models.contribution.Contribution"]
    ] = relationship(
        "app.db.models.contribution.Contribution",
        secondary=affiliations_table,
        lazy="raise",
        back_populates="affiliations",
    )

    def ensure_self_identifier(self) -> None:
        """
        Ensure that organizations from certain sources always have a matching identifier
        (type == source, value == source_identifier).
        """
        source_type_map = {
            "hal": OrganizationIdentifier.IdentifierType.HAL,
            "openalex": OrganizationIdentifier.IdentifierType.OPEN_ALEX,
            "scopus": OrganizationIdentifier.IdentifierType.SCOPUS,
        }
        if self.source not in source_type_map:
            return

        if self.source_identifier is None or str(self.source_identifier).strip() == "":
            raise ValueError("source_identifier is empty")

        identifier_type = source_type_map[self.source]

        if not any(
            ident.type == identifier_type.value
            and ident.value == self.source_identifier
            for ident in (self.identifiers or [])
        ):
            self.identifiers.append(
                OrganizationIdentifier(
                    type=identifier_type.value, value=self.source_identifier
                )
            )
