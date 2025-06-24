from dataclasses import dataclass


@dataclass(frozen=True)
class OrganizationInformations:
    """
    Informations about an organization
    """

    name: str | None = None
    identifier: str | None = None
    source: str | None = None
