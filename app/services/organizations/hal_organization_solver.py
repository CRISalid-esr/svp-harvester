import aiohttp
from loguru import logger
from app.db.models.organization import Organization
from app.services.concepts.dereferencing_error import DereferencingError
from app.services.organizations.organization_solver import OrganizationSolver


class HalOrganizationSolver(OrganizationSolver):
    """
    Hal organization solver
    """

    URL = "https://api.archives-ouvertes.fr/ref/structure/?q=docid:{}&wt=json&fl=*"

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
                    return Organization(
                        source="hal",
                        source_identifier=organization_id,
                        name=data["response"]["docs"][0]["name_s"],
                    )

        except aiohttp.ClientError as error:
            raise DereferencingError(
                "Endpoint failure while dereferencing HAL"
                f" organization {organization_id} with message {error}"
            ) from error
