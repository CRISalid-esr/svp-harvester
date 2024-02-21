import asyncio
from socket import timeout
from typing import List

import aiohttp
from app.db.models.organization import Organization
from app.db.models.organization_identifier import OrganizationIdentifier
from app.services.organizations.organization_solver import OrganizationSolver


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

    async def solve(self, organization_id: str) -> Organization:
        """
        Solves an organization from an organization id
        :param organization_id: id of the organization
        :return: organization
        """
        raise NotImplementedError("RorOrganizationSolver.solve")

    async def solve_identities(
        self, organization_id: str, seen: List[str]
    ) -> tuple[List[OrganizationIdentifier], List[str]]:
        """
        Solves the identities of an organization and search for more identifiers
        :param organization: organization
        :return: OrganizationIdentifier, seen identifiers updated list
        """
        new_identifiers = [OrganizationIdentifier(type="ror", value=organization_id)]
        seen.append("ror")
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=float(2))
            ) as session:
                async with session.get(self.URL.format(organization_id)) as response:
                    if not 200 <= response.status < 300:
                        raise timeout(
                            f"Endpoint returned status {response.status}"
                            f" while dereferencing ROR organization {organization_id}"
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

        # If the request fails, return the new identifiers with only the idref identifier
        except aiohttp.ClientError:
            return new_identifiers, seen
        except asyncio.TimeoutError:
            return new_identifiers, seen
