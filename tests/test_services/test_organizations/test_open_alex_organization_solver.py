from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, Mock

from app.db.models.organization_identifier import OrganizationIdentifier
from app.services.errors.dereferencing_error import DereferencingError
from app.services.organizations.open_alex_organization_solver import (
    OpenAlexOrganizationSolver,
)
from app.services.organizations.organization_informations import (
    OrganizationInformations,
)


# disable AUTOUSE fixture from tests/fixtures/organizations_fixtures.py
@pytest.fixture(name="mock_openalex_organization_solver", autouse=True)
def _disable_autouse_mock_openalex_organization_solver():
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
        self._response = response
        self.get = Mock(return_value=response)


@pytest.fixture()
def openalex_payload():
    # Minimal-but-realistic subset from your attached payload
    return {
        "id": "https://openalex.org/I4210091016",
        "display_name": "Sociétés, Acteurs, Gouvernement en Europe",
        "type": "facility",
        "ids": {
            "openalex": "https://openalex.org/I4210091016",
            "ror": "https://ror.org/00bhwwh42",
            "wikidata": None,
            "wikipedia": None,
        },
        "geo": {
            "city": "Strasbourg",
            "country": "France",
            "country_code": "FR",
            "geonames_city_id": "2973783",
            "latitude": 48.583919525146484,
            "longitude": 7.745530128479004,
        },
        "homepage_url": "http://sage.unistra.fr/en/",
        "works_count": 2657,
        "cited_by_count": 9757,
    }


@pytest.mark.asyncio
async def test_openalex_solver_happy_path_deref_ror(monkeypatch, openalex_payload):
    """
    GIVEN an OpenAlex institution with ids.ror
    WHEN solve() is called
    THEN it builds an Organization, adds open_alex self-id,
         and merges identifiers returned by deep deref (ROR).
    """
    response = _FakeResponse(status=200, payload=openalex_payload)
    fake_session = _FakeSession(response)

    from app.http.aio_http_client_manager import AioHttpClientManager

    monkeypatch.setattr(
        AioHttpClientManager, "get_session", AsyncMock(return_value=fake_session)
    )

    # Patch deep deref for ROR
    from app.services.organizations import organization_factory

    deref_identifiers = [
        OrganizationIdentifier(type="ror", value="00bhwwh42"),
        OrganizationIdentifier(type="wikidata", value="Q999"),
    ]
    monkeypatch.setattr(
        organization_factory.OrganizationFactory,
        "solve_identifier",
        AsyncMock(return_value=(deref_identifiers, ["open_alex", "ror", "wikidata"])),
    )

    solver = OpenAlexOrganizationSolver(timeout=1)
    org = await solver.solve(
        OrganizationInformations(
            name="Sociétés, Acteurs, Gouvernement en Europe",
            identifier="https://openalex.org/I4210091016",
            source="openalex",
        )
    )

    assert org.source == "openalex"
    assert org.source_identifier == "https://openalex.org/I4210091016"
    assert org.name == "Sociétés, Acteurs, Gouvernement en Europe"
    assert org.type == "laboratory"  # facility -> laboratory mapping in TYPE_MAPPING

    received = {(i.type, i.value) for i in org.identifiers}

    # Always has OpenAlex self-id added explicitly
    assert (
        "open_alex",
        "I4210091016",
    ) in received  # normalized by OrganizationIdentifier regex

    # Deep deref merged
    assert ("ror", "00bhwwh42") in received
    assert ("wikidata", "Q999") in received

    # Ensure OpenAlex endpoint called with the ID part only
    assert fake_session.get.call_count == 1
    called_url = fake_session.get.call_args.args[0]
    assert called_url.endswith("/I4210091016")


@pytest.mark.asyncio
async def test_openalex_solver_deref_failure_falls_back_to_raw_ror(
    monkeypatch, openalex_payload
):
    """
    GIVEN ids.ror, but deep deref fails
    WHEN solve() is called
    THEN it falls back to storing the raw ROR identifier anyway.
    """
    response = _FakeResponse(status=200, payload=openalex_payload)
    fake_session = _FakeSession(response)

    from app.http.aio_http_client_manager import AioHttpClientManager

    monkeypatch.setattr(
        AioHttpClientManager, "get_session", AsyncMock(return_value=fake_session)
    )

    from app.services.organizations import organization_factory

    monkeypatch.setattr(
        organization_factory.OrganizationFactory,
        "solve_identifier",
        AsyncMock(side_effect=DereferencingError("ROR failed")),
    )

    solver = OpenAlexOrganizationSolver(timeout=1)
    org = await solver.solve(
        OrganizationInformations(
            identifier="https://openalex.org/I4210091016", source="openalex"
        )
    )

    got = {(i.type, i.value) for i in org.identifiers}
    # normalized by regex
    assert ("ror", "00bhwwh42") in got


@pytest.mark.asyncio
async def test_openalex_solver_non_2xx_raises(monkeypatch, openalex_payload):
    """
    GIVEN OpenAlex endpoint returns non-2xx
    WHEN solve() is called
    THEN it raises DereferencingError
    """
    response = _FakeResponse(status=500, payload=openalex_payload)
    fake_session = _FakeSession(response)

    from app.http.aio_http_client_manager import AioHttpClientManager

    monkeypatch.setattr(
        AioHttpClientManager, "get_session", AsyncMock(return_value=fake_session)
    )

    solver = OpenAlexOrganizationSolver(timeout=1)
    with pytest.raises(DereferencingError):
        await solver.solve(
            OrganizationInformations(
                identifier="https://openalex.org/I4210091016", source="openalex"
            )
        )


@pytest.mark.asyncio
async def test_openalex_solver_missing_display_name_uses_default(
    monkeypatch, openalex_payload
):
    """
    GIVEN payload without display_name
    WHEN solve() is called
    THEN name becomes 'No OpenAlex organization name' (current code behavior)
    """
    payload = dict(openalex_payload)
    payload.pop("display_name", None)

    response = _FakeResponse(status=200, payload=payload)
    fake_session = _FakeSession(response)

    from app.http.aio_http_client_manager import AioHttpClientManager

    monkeypatch.setattr(
        AioHttpClientManager, "get_session", AsyncMock(return_value=fake_session)
    )

    solver = OpenAlexOrganizationSolver(timeout=1)
    org = await solver.solve(
        OrganizationInformations(
            identifier="https://openalex.org/I4210091016", source="openalex"
        )
    )
    assert org.name == "No OpenAlex organization name"


@pytest.mark.asyncio
async def test_openalex_solver_should_save_ids_openalex_and_ror(
    monkeypatch, openalex_payload
):
    """
    This test is intended to catch the mapping bug in IDENTITIFIERS_TO_BE_SAVED:
      - the OpenAlex payload uses ids['openalex'] (not 'open_alex')
      - and ror should map to type='ror' (not 'open_alex').

    EXPECTED (after fix):
      - an identifier (type='open_alex', value='I4210091016' or full URL normalized)
      - an identifier (type='ror', value='00bhwwh42')

    Current code will NOT add these via the saving loop.
    """
    response = _FakeResponse(status=200, payload=openalex_payload)
    fake_session = _FakeSession(response)

    from app.http.aio_http_client_manager import AioHttpClientManager

    monkeypatch.setattr(
        AioHttpClientManager, "get_session", AsyncMock(return_value=fake_session)
    )

    # Disable deep deref so we only test "save ids" loop
    from app.services.organizations import organization_factory

    monkeypatch.setattr(
        organization_factory.OrganizationFactory,
        "solve_identifier",
        AsyncMock(return_value=([], ["open_alex"])),
    )

    solver = OpenAlexOrganizationSolver(timeout=1)
    org = await solver.solve(
        OrganizationInformations(
            identifier="https://openalex.org/I4210091016", source="openalex"
        )
    )

    got = {(i.type, i.value) for i in org.identifiers}

    # self identifier is added regardless
    assert ("open_alex", "I4210091016") in got

    # the "save ids" loop SHOULD add ror too (after fixing mapping)
    assert ("ror", "00bhwwh42") in got
