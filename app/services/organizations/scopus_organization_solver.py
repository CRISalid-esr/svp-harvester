from typing import List

from app.db.models.organization import Organization
from app.db.models.organization_identifier import OrganizationIdentifier
from app.services.organizations.organization_informations import (
    OrganizationInformations,
)
from app.services.organizations.organization_solver import OrganizationSolver


class ScopusOrganizationSolver(OrganizationSolver):
    """
    Scopus organization solver
    """

    URL = "https://api.elsevier.com/"

    async def solve(
        self,
        organization_information: OrganizationInformations,
    ) -> Organization:
        """
        Solves an organization from an organization id
        :param organization_id: id of the organization
        :return: organization
        """
        organization = Organization(
            source="scopus",
            source_identifier=organization_information.identifier,
            name=organization_information.name,
            type="institution",
        )
        organization.identifiers.append(
            OrganizationIdentifier(
                type="scopus", value=organization_information.identifier
            )
        )
        return organization

    async def solve_identities(
        self,
        organization_information: OrganizationIdentifier,
        seen: List[str],
    ) -> tuple[List[OrganizationIdentifier], List[str]]:
        raise NotImplementedError("ScopusOrganizationSolver.solve_identities")
