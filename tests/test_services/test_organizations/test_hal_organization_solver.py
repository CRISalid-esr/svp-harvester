from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from app.db.models.organization_identifier import OrganizationIdentifier
from app.services.errors.dereferencing_error import DereferencingError
from app.services.organizations.hal_organization_solver import HalOrganizationSolver
from app.services.organizations.organization_informations import (
    OrganizationInformations,
)


# disable the AUTOUSE fixture from tests/fixtures/organizations_fixtures.py
@pytest.fixture(name="mock_hal_organization_solver", autouse=True)
def _disable_autouse_mock_hal_organization_solver():
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
        self.get = Mock(return_value=response)  # returns async context manager response


def _hal_payload(doc: dict) -> dict:
    # Matches what HalOrganizationSolver expects:
    # data["response"]["docs"][0]
    return {"response": {"docs": [doc]}}


async def test_hal_solver_happy_path_deref_ror_and_save_ids(monkeypatch):
    """
    GIVEN a HAL org response containing name_s, type_s, and identifiers including ror_s/idref_s/isni_s/rnsr_s
    WHEN HalOrganizationSolver.solve() is called
    THEN it builds an Organization with correct type mapping, adds hal self id,
         saves all identifiers, and merges identifiers returned by deep deref (ROR).
    """
    # HAL doc with a ROR to be dereferenced + identifiers to be saved
    doc = {
        "name_s": "Sociétés, Acteurs, Gouvernement en Europe",
        "type_s": "laboratory",
        "ror_s": ["https://ror.org/00bhwwh42"],
        "idref_s": ["176967214"],
        "isni_s": ["0000000122597504"],
        "rnsr_s": ["201320506M"],
    }
    response = _FakeResponse(status=200, payload=_hal_payload(doc))
    fake_session = _FakeSession(response)

    # Patch HTTP session
    from app.http.aio_http_client_manager import AioHttpClientManager

    monkeypatch.setattr(
        AioHttpClientManager, "get_session", AsyncMock(return_value=fake_session)
    )

    # Patch deep deref call: OrganizationFactory.solve_identifier()
    from app.services.organizations import organization_factory

    deref_identifiers = [
        OrganizationIdentifier(type="ror", value="00bhwwh42"),
        OrganizationIdentifier(type="wikidata", value="Q123"),
    ]
    monkeypatch.setattr(
        organization_factory.OrganizationFactory,
        "solve_identifier",
        AsyncMock(return_value=(deref_identifiers, ["hal", "ror", "wikidata"])),
    )

    solver = HalOrganizationSolver(timeout=1)
    org = await solver.solve(
        OrganizationInformations(identifier="217511", source="hal")
    )

    assert org.source == "hal"
    assert org.source_identifier == "217511"
    assert org.name == "Sociétés, Acteurs, Gouvernement en Europe"
    assert org.type == "laboratory"  # from TYPE_MAPPING

    # identifiers as (type, value) for asserts
    received_identifiers = {(i.type, i.value) for i in org.identifiers}

    # Always has HAL self-id
    assert ("hal", "217511") in received_identifiers

    # Saved identifiers
    assert ("idref", "176967214") in received_identifiers
    assert ("isni", "0000000122597504") in received_identifiers
    assert (
        "nns",
        "201320506M",
    ) in received_identifiers  # RNSR is mapped to IdentifierType.RNSR.value == "nns"

    # Dereferenced identifiers merged
    assert ("ror", "00bhwwh42") in received_identifiers
    assert ("wikidata", "Q123") in received_identifiers

    # Make sure HAL endpoint called with expected URL
    assert fake_session.get.call_count == 1
    called_url = fake_session.get.call_args.args[0]
    assert "api.archives-ouvertes.fr" in called_url
    assert "docid:217511" in called_url


async def test_hal_solver_deref_failure_falls_back_to_raw_identifier(monkeypatch):
    """
    GIVEN HAL response with ror_s, but deep deref fails
    WHEN solve() is called
    THEN it still adds OrganizationIdentifier(type='ror', value=code) as fallback.
    """
    doc = {
        "name_s": "Test org",
        "type_s": "laboratory",
        "ror_s": ["https://ror.org/00bhwwh42"],
    }
    response = _FakeResponse(status=200, payload=_hal_payload(doc))
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

    solver = HalOrganizationSolver(timeout=1)
    org = await solver.solve(
        OrganizationInformations(identifier="217511", source="hal")
    )

    received = {(i.type, i.value) for i in org.identifiers}

    # fallback keeps the code it extracted (first element)
    # note: OrganizationIdentifier normalizes ror URLs, so this ends up as "00bhwwh42"
    assert ("ror", "00bhwwh42") in received


async def test_hal_solver_non_2xx_raises(monkeypatch):
    """
    GIVEN HAL endpoint returns non-2xx
    WHEN solve() is called
    THEN it raises DereferencingError
    """
    response = _FakeResponse(status=500, payload={"error": "boom"})
    fake_session = _FakeSession(response)

    from app.http.aio_http_client_manager import AioHttpClientManager

    monkeypatch.setattr(
        AioHttpClientManager, "get_session", AsyncMock(return_value=fake_session)
    )

    solver = HalOrganizationSolver(timeout=1)

    with pytest.raises(DereferencingError):
        await solver.solve(OrganizationInformations(identifier="217511", source="hal"))


async def test_hal_solver_missing_name_raises(monkeypatch):
    """
    GIVEN HAL response has no name_s
    WHEN solve() is called
    THEN it raises DereferencingError
    """
    doc = {
        "type_s": "laboratory",
        "ror_s": ["https://ror.org/00bhwwh42"],
    }
    response = _FakeResponse(status=200, payload=_hal_payload(doc))
    fake_session = _FakeSession(response)

    from app.http.aio_http_client_manager import AioHttpClientManager

    monkeypatch.setattr(
        AioHttpClientManager, "get_session", AsyncMock(return_value=fake_session)
    )

    solver = HalOrganizationSolver(timeout=1)

    with pytest.raises(DereferencingError, match="has no name"):
        await solver.solve(OrganizationInformations(identifier="217511", source="hal"))
