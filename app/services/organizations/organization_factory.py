from app.db.models.organization import Organization
from app.services.organizations.hal_organization_solver import HalOrganizationSolver
from app.services.organizations.organization_solver import OrganizationSolver


class OrganizationFactory:
    """
    Solves an organization from an organization id and an source by calling the appropriate solver
    """

    @staticmethod
    async def solve(organization_id: str, organization_source: str) -> Organization:
        """
        Solves an organization from an organization id and a source
        :param organization_id: id of the organization
        :param organization_source: source of the organization

        :return: organization
        """
        solver: OrganizationSolver = OrganizationFactory._create_solver(
            organization_source
        )
        organization = await solver.solve(organization_id)
        return organization

    @classmethod
    def _create_solver(cls, organization_source) -> OrganizationSolver:
        if organization_source == "hal":
            return HalOrganizationSolver()
        raise ValueError(f"Unknown organization source: {organization_source}")
