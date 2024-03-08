from typing import List

from app.config import get_app_settings
from app.db.models.organization import Organization
from app.db.models.organization_identifier import OrganizationIdentifier
from app.services.organizations.hal_organization_solver import HalOrganizationSolver
from app.services.organizations.idref_organization_solver import IdrefOrganizationSolver
from app.services.organizations.organization_data_class import OrganizationInformations
from app.services.organizations.organization_solver import OrganizationSolver
from app.services.organizations.ror_organization_solver import RorOrganizationSolver
from app.services.organizations.scopus_organization_solver import (
    ScopusOrganizationSolver,
)


class OrganizationFactory:
    """
    Solves an organization from an organization id and an source by calling the appropriate solver
    """

    @staticmethod
    async def solve(
        organization_information: OrganizationInformations,
    ) -> Organization:
        """
        Solves an organization from an organization id and a source
        :param organization_id: id of the organization
        :param organization_source: source of the organization

        :return: organization
        """
        solver: OrganizationSolver = OrganizationFactory._create_solver(
            organization_information.source
        )
        organization = await solver.solve(organization_information)
        return organization

    @staticmethod
    async def solve_identities(
        organization_information: OrganizationInformations,
        seen: List[str],
    ) -> tuple[OrganizationIdentifier, List[str]]:
        """
        Solves the identities of an organization if not already seen
        :param organization_id: id of the organization
        :param organization_source: source of the organization

        :return: organization identifier, seen identifiers updated list
        """
        if organization_information.source in seen:
            return None
        solver: OrganizationSolver = OrganizationFactory._create_solver(
            organization_information.source
        )
        organization, seen = await solver.solve_identities(
            organization_information, seen
        )
        return organization, seen

    @classmethod
    def _create_solver(cls, organization_source) -> OrganizationSolver:
        settings = get_app_settings()
        if organization_source == "hal":
            return HalOrganizationSolver(timeout=settings.hal_organizations_timeout)
        if organization_source == "idref":
            return IdrefOrganizationSolver(timeout=settings.idref_organizations_timeout)
        if organization_source == "ror":
            return RorOrganizationSolver(timeout=settings.ror_organizations_timeout)
        if organization_source == "scopus":
            return ScopusOrganizationSolver(
                timeout=settings.scopus_organizations_timeout
            )
        raise ValueError(f"Unknown organization source: {organization_source}")
