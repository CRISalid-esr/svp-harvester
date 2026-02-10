from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from app.db.models.organization_identifier import OrganizationIdentifier
from app.http.aio_http_client_manager import AioHttpClientManager
from app.services.organizations.organization_informations import (
    OrganizationInformations,
)
from app.services.organizations.ror_organization_solver import RorOrganizationSolver


# disable AUTOUSE fixture from tests/fixtures/organizations_fixtures.py
@pytest.fixture(name="mock_ror_organization_solver", autouse=True)
def _disable_autouse_mock_ror_organization_solver():
    return


class _FakeResponse:
    def __init__(self, status: int, payload: dict):
        self.status = status
        self._payload = payload
        self.release = AsyncMock()

    async def json(self):
        return self._payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _FakeSession:
    def __init__(self, response: _FakeResponse):
        self.get = Mock(return_value=response)


@pytest.fixture(name="ror_payload")
def fixture_ror_payload():
    # Minimal subset of ROR payload.
    return {
        "id": "https://ror.org/035j0tq82",
        "status": "active",
        "types": ["company", "funder"],
        "established": 1988,
        "external_ids": [
            {
                "all": ["501100003951", "501100003187"],
                "preferred": "501100003951",
                "type": "fundref",
            },
            {"all": ["grid.89485.38"], "preferred": "grid.89485.38", "type": "grid"},
            {"all": ["0000 0004 0600 5611"], "preferred": None, "type": "isni"},
            {"all": ["Q1431486"], "preferred": None, "type": "wikidata"},
        ],
        "locations": [
            {
                "geonames_details": {
                    "continent_code": "EU",
                    "continent_name": "Europe",
                    "country_code": "FR",
                    "country_name": "France",
                    "country_subdivision_code": "IDF",
                    "country_subdivision_name": "Île-de-France",
                    "lat": 48.85341,
                    "lng": 2.3488,
                    "name": "Paris",
                },
                "geonames_id": 2988507,
            }
        ],
    }


@pytest.mark.asyncio
async def test_ror_solve_identifier_builds_ror_identifier_with_extra_information_and_wikidata(
    monkeypatch, ror_payload
):
    """
    GIVEN a ROR payload with locations and external_ids including wikidata
    WHEN solve_identifier() is called
    THEN it returns:
      - a 'ror' identifier with extra_information.geonames_locations flattened
      - additional mapped identifiers (wikidata) extracted from external_ids
      - seen updated accordingly
    """
    response = _FakeResponse(status=200, payload=ror_payload)
    fake_session = _FakeSession(response)

    from app.http.aio_http_client_manager import AioHttpClientManager

    monkeypatch.setattr(
        AioHttpClientManager, "get_session", AsyncMock(return_value=fake_session)
    )

    solver = RorOrganizationSolver(timeout=1)
    identifiers, seen = await solver.solve_identifier(
        OrganizationInformations(
            name=None, identifier="https://ror.org/035j0tq82", source="ror"
        ),
        seen=[],
    )

    # must include ror
    ror_idents = [
        i
        for i in identifiers
        if i.type == OrganizationIdentifier.IdentifierType.ROR.value
    ]
    assert len(ror_idents) == 1
    ror_ident = ror_idents[0]

    # normalized by OrganizationIdentifier regex: https://ror.org/035j0tq82 -> 035j0tq82
    assert ror_ident.value == "035j0tq82"

    # extra_information should include republish-friendly fields
    extra = ror_ident.extra_information
    assert extra["status"] == "active"
    assert extra["types"] == ["company", "funder"]
    assert extra["established"] == 1988

    # geonames flattening
    assert "geonames_locations" in extra
    assert isinstance(extra["geonames_locations"], list)
    assert extra["geonames_locations"] == [
        {
            "continent_code": "EU",
            "continent_name": "Europe",
            "country_code": "FR",
            "country_name": "France",
            "country_subdivision_code": "IDF",
            "country_subdivision_name": "Île-de-France",
            "lat": 48.85341,
            "lng": 2.3488,
            "name": "Paris",
            "geonames_id": 2988507,
        }
    ]

    # external_ids mapping: only wikidata is enabled in your solver mapping
    wikidata = [
        (i.type, i.value)
        for i in identifiers
        if i.type == OrganizationIdentifier.IdentifierType.WIKIDATA.value
    ]
    assert wikidata == [
        (OrganizationIdentifier.IdentifierType.WIKIDATA.value, "Q1431486")
    ]

    # seen must include 'ror' and 'wikidata'
    assert OrganizationIdentifier.IdentifierType.ROR.value in seen
    assert OrganizationIdentifier.IdentifierType.WIKIDATA.value in seen

    # ensure correct endpoint usage (URL.format(identifier))
    assert fake_session.get.call_count == 1
    called_url = fake_session.get.call_args.args[0]
    assert called_url.endswith("/035j0tq82")


@pytest.mark.asyncio
async def test_ror_solve_identifier_dedups_external_ids(monkeypatch, ror_payload):
    """
    GIVEN external_ids contains duplicate wikidata values
    WHEN solve_identifier() is called
    THEN wikidata identifier is only created once (dedup by (type,value)).
    """
    payload = dict(ror_payload)
    payload["external_ids"] = list(payload["external_ids"]) + [
        {"all": ["Q1431486"], "preferred": None, "type": "wikidata"}
    ]

    response = _FakeResponse(status=200, payload=payload)
    fake_session = _FakeSession(response)

    monkeypatch.setattr(
        AioHttpClientManager, "get_session", AsyncMock(return_value=fake_session)
    )

    solver = RorOrganizationSolver(timeout=1)
    identifiers, _ = await solver.solve_identifier(
        OrganizationInformations(
            name=None, identifier="https://ror.org/035j0tq82", source="ror"
        ),
        seen=[],
    )

    wikidata = [
        (i.type, i.value)
        for i in identifiers
        if i.type == OrganizationIdentifier.IdentifierType.WIKIDATA.value
    ]
    assert wikidata == [
        (OrganizationIdentifier.IdentifierType.WIKIDATA.value, "Q1431486")
    ]


@pytest.mark.asyncio
async def test_ror_solve_identifier_non_2xx_raises(monkeypatch, ror_payload):
    """
    GIVEN ROR endpoint returns non-2xx
    WHEN solve_identifier() is called
    THEN it raises (socket) timeout (current implementation).
    """
    response = _FakeResponse(status=500, payload=ror_payload)
    fake_session = _FakeSession(response)

    monkeypatch.setattr(
        AioHttpClientManager, "get_session", AsyncMock(return_value=fake_session)
    )

    solver = RorOrganizationSolver(timeout=1)
    with pytest.raises(
        Exception
    ):  # socket.timeout is a bit awkward to import reliably here
        await solver.solve_identifier(
            OrganizationInformations(
                name=None, identifier="https://ror.org/035j0tq82", source="ror"
            ),
            seen=[],
        )
