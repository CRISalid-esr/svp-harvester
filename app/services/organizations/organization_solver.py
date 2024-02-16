from abc import ABC, abstractmethod

from app.db.models.organization import Organization


class OrganizationSolver(ABC):
    """
    Abstract mother class for organization solvers
    """

    @abstractmethod
    async def solve(self, organization_id: str) -> Organization:
        """
        Solves an organization from an organization id
        :param organization_id: id of the organization
        :return: organization
        """
