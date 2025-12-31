# file: app/services/organizations/dummy_organization_solver.py

from typing import List

from app.db.models.organization import Organization
from app.db.models.organization_identifier import OrganizationIdentifier
from app.services.errors.dereferencing_error import DereferencingError
from app.services.organizations.organization_informations import (
    OrganizationInformations,
)
from app.services.organizations.organization_solver import OrganizationSolver


class DummyOrganizationSolver(OrganizationSolver):
    """
    Dummy organization solver that creates an organization from the given information
    without making any remote call.
    """

    async def solve(
        self, organization_information: OrganizationInformations
    ) -> Organization:
        if (
            not organization_information.identifier
            and not organization_information.name
        ):
            raise DereferencingError("Dummy solver needs at least a name or identifier")

        source = organization_information.source or "no-source"
        identifier = (
            organization_information.identifier
            or organization_information.name.replace(" ", "_").lower()
        )
        name = (
            organization_information.name
            or organization_information.identifier
            or "Unnamed organization"
        )

        organization = Organization(
            source=source,
            source_identifier=identifier,
            name=name,
            type="unknown",  # or choose a default like "institution"
        )

        if not source == "no-source":
            organization.identifiers.append(
                OrganizationIdentifier(type=source, value=identifier)
            )
        return organization

    async def solve_identifier(
        self,
        organization_information: OrganizationInformations,
        seen: List[str],
    ) -> tuple[List[OrganizationIdentifier], List[str]]:
        if not organization_information.source:
            raise DereferencingError("Source is required to resolve identities")
        if organization_information.source in seen:
            return [], seen

        identifier = organization_information.identifier or "no-id"
        org_id = OrganizationIdentifier(
            type=organization_information.source,
            value=identifier,
        )
        seen.append(organization_information.source)
        return [org_id], seen
