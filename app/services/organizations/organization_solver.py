from abc import ABC, abstractmethod
from typing import List

from app.db.models.organization import Organization
from app.db.models.organization_identifier import OrganizationIdentifier


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

    @abstractmethod
    async def solve_identities(
        self, organization_id: str, seen: List[str]
    ) -> tuple[List[OrganizationIdentifier], List[str]]:
        """
        Solves the identities of an organization
        :param organization: organization
        :return: organization identifier, seen identifiers updated list
        """
