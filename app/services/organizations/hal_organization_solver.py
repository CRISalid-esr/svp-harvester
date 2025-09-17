from typing import List

from aiohttp import ClientTimeout

from app.db.models.organization import Organization
from app.db.models.organization_identifier import OrganizationIdentifier
from app.http.aio_http_client_manager import AioHttpClientManager
from app.services.errors.dereferencing_error import (
    DereferencingError,
    handle_organization_dereferencing_error,
)
from app.services.organizations import (  # pylint: disable=cyclic-import
    organization_factory,
)
from app.services.organizations.organization_informations import (
    OrganizationInformations,
)
from app.services.organizations.organization_solver import OrganizationSolver


# pylint: disable=duplicate-code
class HalOrganizationSolver(OrganizationSolver):
    """
    Hal organization solver
    """

    URL = "https://api.archives-ouvertes.fr/ref/structure/?q=docid:{}&wt=json&fl=*"

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

    @handle_organization_dereferencing_error("HAL")
    async def solve(
        self, organization_information: OrganizationInformations
    ) -> Organization:
        """
        Solves an organization from an organization id, with deep search
        :param organization_information.identifier: id of the organization
        :return: Organization
        """
        session = await AioHttpClientManager.get_session()
        request_timeout = ClientTimeout(total=float(self.timeout))
        async with session.get(
            self.URL.format(organization_information.identifier),
            timeout=request_timeout,
        ) as response:
            if not 200 <= response.status < 300:
                await response.release()
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
                if (source not in seen) and (key in data["response"]["docs"][0]):
                    code = data["response"]["docs"][0][key][0]
                    try:
                        (
                            identifiers,
                            seen,
                        ) = await organization_factory.OrganizationFactory.solve_identities(
                            OrganizationInformations(identifier=code, source=source),
                            seen,
                        )
                        new_identifiers.extend(identifiers)
                    except (ValueError, DereferencingError):
                        new_identifiers.append(
                            OrganizationIdentifier(type=source, value=code)
                        )
                        seen.append(source)
            for key, source in self.IDENTITY_SAVE.items():
                if (source not in seen) and (key in data["response"]["docs"][0]):
                    code = data["response"]["docs"][0][key][0]
                    new_identifiers.append(
                        OrganizationIdentifier(type=source, value=code)
                    )
                    seen.append(source)
            org.identifiers.extend(new_identifiers)
            return org

    async def solve_identities(
        self, organization_information: OrganizationInformations, seen
    ) -> tuple[List[OrganizationIdentifier], List[str]]:
        """
        Solves the identities of an organization
        :param organization: organization
        :return: organization identifier, seen identifiers updated list
        """
        raise NotImplementedError("Not implemented yet")
