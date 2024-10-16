import asyncio
from typing import List

import aiohttp
from app.services.organizations.organization_data_class import OrganizationInformations

from app.db.models.organization import Organization
from app.db.models.organization_identifier import OrganizationIdentifier
from app.services.concepts.dereferencing_error import DereferencingError
from app.services.organizations import (  # pylint: disable=cyclic-import
    organization_factory,
)
from app.services.organizations.organization_solver import OrganizationSolver


# pylint: disable=duplicate-code
class HalOrganizationSolver(OrganizationSolver):
    """
    Hal organization solver
    """

    URL = "https://api.archives-ouvertes.fr/ref/structure/?q=docid:{}&wt=json&fl=*"

    # values could be
    # "idref_s": "idref",
    # "ror_s": "ror",
    IDENTITY_DEEP_SEARCH = {}
    IDENTITY_SAVE = {
        "isni_s": "isni",
        "rnsr_s": "rnsr",
        "idref_s": "idref",
        "ror_s": "ror",
    }

    TYPE_MAPPING = {
        "institution": "institution",
        "laboratory": "laboratory",
        "regroupinstitution": "institution_group",
        "regrouplaboratory": "laboratory_group",
        "researchteam": "research_team",
        "department": "research_team_group",
    }

    async def solve(
        self, organization_information: OrganizationInformations
    ) -> Organization:
        """
        Solves an organization from an organization id, with deep search
        :param organization_information.identifier: id of the organization
        :return: Organization
        """
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=float(self.timeout))
            ) as session:
                async with session.get(
                    self.URL.format(organization_information.identifier)
                ) as response:
                    if not 200 <= response.status < 300:
                        raise DereferencingError(
                            f"Endpoint returned status {response.status}"
                            f" while dereferencing HAL organization"
                            f" {organization_information.identifier}"
                        )
                    data = await response.json()
                    name = data["response"]["docs"][0].get("name_s", None)
                    if not name:
                        raise DereferencingError(
                            f"HAL organization {organization_information.identifier}"
                            " has no name"
                        )
                    org = Organization(
                        source="hal",
                        source_identifier=organization_information.identifier,
                        name=name,
                        type=self.TYPE_MAPPING[data["response"]["docs"][0]["type_s"]],
                    )
                    org.identifiers.append(
                        OrganizationIdentifier(
                            type="hal", value=organization_information.identifier
                        )
                    )
                    seen = ["hal"]
                    new_identifiers = []
                    for key, source in self.IDENTITY_DEEP_SEARCH.items():
                        if (source not in seen) and (
                            key in data["response"]["docs"][0]
                        ):
                            code = data["response"]["docs"][0][key][0]
                            (
                                identifiers,
                                seen,
                            ) = await organization_factory.OrganizationFactory.solve_identities(
                                OrganizationInformations(
                                    identifier=code, source=source
                                ),
                                seen,
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
                    org.identifiers.extend(new_identifiers)
                    return org

        except aiohttp.ClientError as error:
            raise DereferencingError(
                "Endpoint failure while dereferencing HAL"
                f" organization {organization_information.identifier} with message {error}"
            ) from error
        except asyncio.TimeoutError as error:
            raise DereferencingError(
                "Timeout while dereferencing HAL"
                f" organization {organization_information.identifier} with message {error}"
            ) from error

    async def solve_identities(
        self, organization_information: OrganizationInformations, seen
    ) -> tuple[List[OrganizationIdentifier], List[str]]:
        """
        Solves the identities of an organization
        :param organization: organization
        :return: organization identifier, seen identifiers updated list
        """
        raise NotImplementedError("Not implemented yet")
