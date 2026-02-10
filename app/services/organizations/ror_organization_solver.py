from typing import List, Tuple, Dict, Any, Set

from aiohttp import ClientTimeout
from loguru import logger

from app.config import get_app_settings
from app.db.models.organization import Organization
from app.db.models.organization_identifier import OrganizationIdentifier
from app.http.aio_http_client_manager import AioHttpClientManager
from app.services.errors.dereferencing_error import (
    handle_organization_dereferencing_error,
    DereferencingError,
)
from app.services.organizations.organization_informations import (
    OrganizationInformations,
)
from app.services.organizations.organization_solver import OrganizationSolver


class RorOrganizationSolver(OrganizationSolver):
    """
    ROR organization solver
    """

    URL = "https://api.ror.org/v2/organizations/{}"

    # ROR external_ids[].type -> OrganizationIdentifier.type
    # 3 of them are commented out because they could return multiple values and
    # complexify the handling of organization states in the knowledge graph.
    IDENTITIFIERS_TO_BE_SAVED = {
        # "isni": OrganizationIdentifier.IdentifierType.ISNI.value,
        # "grid": OrganizationIdentifier.IdentifierType.GRID.value,
        "wikidata": OrganizationIdentifier.IdentifierType.WIKIDATA.value,
        # "fundref": OrganizationIdentifier.IdentifierType.FUNDREF.value,
    }

    @staticmethod
    def _flatten_geonames_locations(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for loc in data.get("locations", []) or []:
            location = (loc or {}).get("geonames_details", {})
            geonames_id = (loc or {}).get("geonames_id")
            if not location or not geonames_id:
                continue
            location["geonames_id"] = geonames_id
            out.append(location)
        return out

    @staticmethod
    def _extract_external_identifiers(data: Dict[str, Any]) -> List[Tuple[str, str]]:
        """
        Returns a list of (type, value) pairs extracted from ROR external_ids.
        """
        pairs: List[Tuple[str, str]] = []
        for item in data.get("external_ids", []) or []:
            ror_type = (item or {}).get("type")
            if not ror_type:
                continue
            mapped = RorOrganizationSolver.IDENTITIFIERS_TO_BE_SAVED.get(
                str(ror_type).lower()
            )
            if not mapped:
                continue

            values = (item or {}).get("all")
            if isinstance(values, list):
                for v in values:
                    if v:
                        pairs.append((mapped, str(v)))
            elif values:
                pairs.append((mapped, str(values)))

        return pairs

    async def solve(
        self, organization_information: OrganizationInformations
    ) -> Organization:
        raise NotImplementedError("RorOrganizationSolver.solve")

    @handle_organization_dereferencing_error("ROR")
    async def solve_identifier(
        self, organization_information: OrganizationInformations, seen: List[str]
    ) -> Tuple[List[OrganizationIdentifier], List[str]]:
        session = await AioHttpClientManager.get_session()

        client_id = get_app_settings().ror_api_client_id
        headers: Dict[str, str] = {}
        if client_id:
            headers["Client-Id"] = str(client_id)
        else:
            logger.warning(
                "ROR client id is not configured (ROR_API_CLIENT_ID). "
                "Requests may be rate-limited."
            )

        ror_id = (organization_information.identifier or "").split("/")[-1]
        if not ror_id:
            raise DereferencingError("ROR identifier is empty")

        async with session.get(
            self.URL.format(ror_id),
            timeout=(ClientTimeout(total=float(self.timeout))),
            headers=headers or None,  # aiohttp accepts None
        ) as response:
            if not 200 <= response.status < 300:
                await response.release()
                raise DereferencingError(
                    f"Endpoint returned status {response.status} while dereferencing "
                    f"ROR organization {organization_information.identifier}"
                )
            data = await response.json()

        ror_identifier = OrganizationIdentifier(
            type=OrganizationIdentifier.IdentifierType.ROR.value,
            value=organization_information.identifier,
            extra_information={
                "geonames_locations": self._flatten_geonames_locations(data),
                "status": data.get("status"),
                "types": data.get("types"),
                "established": data.get("established"),
            },
        )

        new_identifiers: List[OrganizationIdentifier] = [ror_identifier]
        seen.append(OrganizationIdentifier.IdentifierType.ROR.value)

        # Dedup by (type, value)
        dedup: Set[Tuple[str, str]] = {
            (OrganizationIdentifier.IdentifierType.ROR, ror_identifier.value)
        }

        for id_type, id_value in self._extract_external_identifiers(data):
            key = (id_type, id_value)
            if key in dedup:
                continue
            dedup.add(key)
            new_identifiers.append(OrganizationIdentifier(type=id_type, value=id_value))
            if id_type not in seen:
                seen.append(id_type)

        return new_identifiers, seen
