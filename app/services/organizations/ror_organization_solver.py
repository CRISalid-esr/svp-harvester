from socket import timeout
from typing import List

from aiohttp import ClientTimeout

from app.db.models.organization import Organization
from app.db.models.organization_identifier import OrganizationIdentifier
from app.http_client import get_aiohttp_session
from app.services.errors.dereferencing_error import (
    handle_organization_dereferencing_error,
)
from app.services.organizations.organization_informations import (
    OrganizationInformations,
)
from app.services.organizations.organization_solver import OrganizationSolver


# pylint: disable=duplicate-code
class RorOrganizationSolver(OrganizationSolver):
    """
    Ror organization solver
    """

    URL = "https://api.ror.org/organizations/{}"
    IDENTITY_SAVE = {
        "ISNI": "isni",
        "FundRef": "ofr",
        "Wikidata": "wikidata",
        "GRID": "grid",
    }

    async def solve(
        self, organization_information: OrganizationInformations
    ) -> Organization:
        """
        Solves an organization from an organization id
        :param organization_id: id of the organization
        :return: organization
        """
        raise NotImplementedError("RorOrganizationSolver.solve")

    @handle_organization_dereferencing_error("ROR")
    async def solve_identities(
        self, organization_information: OrganizationInformations, seen: List[str]
    ) -> tuple[List[OrganizationIdentifier], List[str]]:
        """
        Solves the identities of an organization and search for more identifiers
        :param organization: organization
        :return: OrganizationIdentifier, seen identifiers updated list
        """
        new_identifiers = [
            OrganizationIdentifier(
                type="ror", value=organization_information.identifier
            )
        ]
        seen.append("ror")
        session = get_aiohttp_session()
        request_timeout = ClientTimeout(total=float(self.timeout))

        async with session.get(
            self.URL.format(organization_information.identifier),
            timeout=request_timeout,
        ) as response:
            if not 200 <= response.status < 300:
                raise timeout(
                    f"Endpoint returned status {response.status}"
                    f" while dereferencing ROR organization"
                    f" {organization_information.identifier}"
                )
            data = await response.json()
            for identifier, source in self.IDENTITY_SAVE.items():
                if identifier in data["external_ids"]:
                    identifier_value = data["external_ids"][identifier]["all"]
                    if isinstance(identifier_value, list):
                        identifier_value = identifier_value[0]
                    new_identifiers.append(
                        OrganizationIdentifier(
                            type=source,
                            value=identifier_value,
                        )
                    )
                    seen.append(source)
        return new_identifiers, seen
