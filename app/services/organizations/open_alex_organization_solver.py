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
class OpenAlexOrganizationSolver(OrganizationSolver):
    """
    OpenAlex organization solver
    """

    URL = "https://api.openalex.org/institutions/{}"

    # OpenAlex responses key -> OrganizationIdentifier.type
    IDENTIFIERS_TO_BE_DEREFERENCED = {
        "ror": OrganizationIdentifier.IdentifierType.ROR.value,
    }

    IDENTIFIERS_TO_BE_SAVED = {
        "openalex": OrganizationIdentifier.IdentifierType.OPEN_ALEX.value,
        "ror": OrganizationIdentifier.IdentifierType.ROR.value,
    }

    TYPE_MAPPING = {
        "education": "institution",
        "healthcare": "organization",
        "company": "organization",
        "archive": "organization",
        "nonprofit": "organization",
        "government": "institution",
        "facility": "laboratory",
        "other": "organization",
        "funder": "organization",
    }

    @handle_organization_dereferencing_error("openalex")
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
            self.URL.format(organization_information.identifier.split("/")[-1]),
            timeout=request_timeout,
        ) as response:
            if not 200 <= response.status < 300:
                await response.release()
                raise DereferencingError(
                    f"Endpoint returned status {response.status}"
                    f" while dereferencing OpenAlex organization"
                    f" {organization_information.identifier}"
                )
            data = await response.json()
            name = data.get("display_name", "No OpenAlex organization name")
            if not name:
                raise DereferencingError(
                    f"OpenAlex organization {organization_information.identifier}"
                    " has no name"
                )
            org = Organization(
                source=organization_information.source,
                source_identifier=organization_information.identifier,
                name=name,
                type=self.TYPE_MAPPING[data.get("type")],
            )
            org.identifiers.append(
                OrganizationIdentifier(
                    type=OrganizationIdentifier.IdentifierType.OPEN_ALEX.value,
                    value=organization_information.identifier,
                )
            )
            seen = [OrganizationIdentifier.IdentifierType.OPEN_ALEX.value]
            new_identifiers = []
            for key, type_ in self.IDENTIFIERS_TO_BE_DEREFERENCED.items():
                if (type_ not in seen) and (key in data.get("ids", {})):
                    code = data.get("ids", {}).get(key, None)
                    if not code:
                        continue
                    try:
                        (
                            identifiers,
                            seen,
                        ) = await organization_factory.OrganizationFactory.solve_identifier(
                            OrganizationInformations(identifier=code, source=type_),
                            seen,
                        )
                        new_identifiers.extend(identifiers)
                    except (ValueError, DereferencingError):
                        new_identifiers.append(
                            OrganizationIdentifier(type=type_, value=code)
                        )
                        seen.append(type_)
            for key, type_ in self.IDENTIFIERS_TO_BE_SAVED.items():
                if (type_ not in seen) and (key in data.get("ids", {})):
                    code = data.get("ids", {}).get(key, None)
                    if not code:
                        continue
                    new_identifiers.append(
                        OrganizationIdentifier(type=type_, value=code)
                    )
                    seen.append(type_)
            org.identifiers.extend(new_identifiers)
            return org

    async def solve_identifier(
        self, organization_information: OrganizationInformations, seen
    ) -> tuple[List[OrganizationIdentifier], List[str]]:
        """
        Solves the identities of an organization
        :param organization: organization
        :return: organization identifier, seen identifiers updated list
        """
        raise NotImplementedError("Not implemented yet")
