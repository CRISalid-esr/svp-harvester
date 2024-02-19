from typing import List
import aiohttp
import app.services.organizations.organization_factory as organization_factory
from app.db.models.organization import Organization
from app.db.models.organization_identifier import OrganizationIdentifier
from app.services.concepts.dereferencing_error import DereferencingError
from app.services.organizations.organization_solver import OrganizationSolver


class HalOrganizationSolver(OrganizationSolver):
    """
    Hal organization solver
    """

    URL = "https://api.archives-ouvertes.fr/ref/structure/?q=docid:{}&wt=json&fl=*"

    IDENTITY_DEEP_SEARCH = {
        "idref_s": "idref",
        "ror_s": "ror",
    }
    IDENTITY_SAVE = {
        "isni_s": "isni",
        "rnsr_s": "rnsr",
    }

    async def solve(self, organization_id: str) -> Organization:
        """
        Solves an organization from an organization id
        :param organization_id: id of the organization
        :return: organization
        """
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=float(2))
            ) as session:
                async with session.get(self.URL.format(organization_id)) as response:
                    if not 200 <= response.status < 300:
                        raise DereferencingError(
                            f"Endpoint returned status {response.status}"
                            f" while dereferencing HAL organization {organization_id}"
                        )
                    data = await response.json()
                    org = Organization(
                        source="hal",
                        source_identifier=organization_id,
                        name=data["response"]["docs"][0]["name_s"],
                        type=data["response"]["docs"][0]["type_s"],
                    )
                    org.identifiers.append(
                        OrganizationIdentifier(type="hal", value=organization_id)
                    )
                    seen = ["hal"]
                    new_identifiers = []
                    for key, source in self.IDENTITY_DEEP_SEARCH.items():
                        if (source not in seen) and (
                            key in data["response"]["docs"][0]
                        ):
                            code = data["response"]["docs"][0][key][0]
                            identifiers, seen = (
                                await organization_factory.OrganizationFactory.solve_identities(
                                    code,
                                    source,
                                    seen,
                                )
                            )
                            new_identifiers.extend(identifiers)
                    for key, source in self.IDENTITY_SAVE.items():
                        if (source not in seen) and (
                            key in data["response"]["docs"][0]
                        ):
                            code = data["response"]["docs"][0][key][0]
                            new_identifiers.append(
                                OrganizationIdentifier(type=source, value=code)
                            )
                            seen.append(source)
                    print("NEW IDENTIFIERS", new_identifiers)
                    org.identifiers.extend(new_identifiers)
                    return org

        except aiohttp.ClientError as error:
            raise DereferencingError(
                "Endpoint failure while dereferencing HAL"
                f" organization {organization_id} with message {error}"
            ) from error

    async def solve_identities(
        self, organization_id: str, seen
    ) -> tuple[List[OrganizationIdentifier], List[str]]:
        """
        Solves the identities of an organization
        :param organization: organization
        :return: organization identifier, seen identifiers updated list
        """
        raise NotImplementedError("Not implemented yet")
