from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, Mock

from app.db.models.organization_identifier import OrganizationIdentifier
from app.services.errors.dereferencing_error import DereferencingError
from app.services.organizations.idref_organization_solver import IdrefOrganizationSolver
from app.services.organizations.organization_informations import (
    OrganizationInformations,
)


# disable AUTOUSE fixture from tests/fixtures/organizations_fixtures.py
@pytest.fixture(name="mock_idref_organization_solver", autouse=True)
def _disable_autouse_mock_idref_organization_solver():
    return


class _FakeResponse:
    def __init__(self, status: int, text_payload: str):
        self.status = status
        self._text = text_payload
        self.release = AsyncMock()

    async def text(self):
        return self._text

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _FakeSession:
    def __init__(self, response: _FakeResponse):
        self._response = response
        self.get = Mock(return_value=response)


@pytest.fixture()
def idref_rdf_xml_minimal():
    # Minimal valid RDF/XML for rdflib.Graph().parse(format="xml")
    # Contains owl:sameAs links similar to your real IdRef example.
    return """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:owl="http://www.w3.org/2002/07/owl#"
    xmlns:foaf="http://xmlns.com/foaf/0.1/">

  <foaf:Organization rdf:about="http://www.idref.fr/027361802/id">
    <owl:sameAs rdf:resource="https://data.hal.science/structure/7550#foaf:Organization"/>
    <owl:sameAs rdf:resource="https://ror.org/002t25c44#foaf:Organization"/>
    <owl:sameAs rdf:resource="http://isni.org/isni/000000012173743X"/>
    <owl:sameAs rdf:resource="http://viaf.org/viaf/143080305"/>
    <owl:sameAs rdf:resource="https://example.org/unknown/thing"/>
  </foaf:Organization>

</rdf:RDF>
"""


@pytest.mark.asyncio
async def test_idref_solver_identifier_normalizes_scanr_prefix(
    monkeypatch, idref_rdf_xml_minimal
):
    """
    GIVEN OrganizationInformations.identifier like 'scanr_idref_027361802'
    WHEN solve_identifier() is called
    THEN it stores idref identifier with value '027361802' and seen contains 'idref'
    """
    response = _FakeResponse(status=200, text_payload=idref_rdf_xml_minimal)
    fake_session = _FakeSession(response)

    from app.http.aio_http_client_manager import AioHttpClientManager

    monkeypatch.setattr(
        AioHttpClientManager, "get_session", AsyncMock(return_value=fake_session)
    )

    # Avoid any deep deref calls (we will mock them anyway)
    from app.services.organizations import organization_factory

    monkeypatch.setattr(
        organization_factory.OrganizationFactory,
        "solve_identifier",
        AsyncMock(return_value=([], ["idref"])),
    )

    solver = IdrefOrganizationSolver(timeout=1)
    identifiers, seen = await solver.solve_identifier(
        OrganizationInformations(
            name="Université Paris 1 Panthéon-Sorbonne",
            identifier="scanr_idref_027361802",
            source="scanr",
        ),
        seen=[],
    )

    received_identifiers = {(i.type, i.value) for i in identifiers}
    assert ("idref", "027361802") in received_identifiers
    assert "idref" in seen

    # ensure request URL uses .rdf
    assert fake_session.get.call_count == 1
    called_url = fake_session.get.call_args.args[0]
    assert called_url.endswith("027361802.rdf")


@pytest.mark.asyncio
async def test_idref_solver_saves_hal_isni_viaf_and_derefs_ror(
    monkeypatch, idref_rdf_xml_minimal
):
    """
    GIVEN IdRef RDF contains sameAs for HAL, ROR, ISNI, VIAF
    WHEN solve_identifier() is called and ROR deref returns extra ids
    THEN it includes idref + hal + isni + viaf and merges deref identifiers.
    """
    response = _FakeResponse(status=200, text_payload=idref_rdf_xml_minimal)
    fake_session = _FakeSession(response)

    from app.http.aio_http_client_manager import AioHttpClientManager

    monkeypatch.setattr(
        AioHttpClientManager, "get_session", AsyncMock(return_value=fake_session)
    )

    from app.services.organizations import organization_factory

    deref_identifiers = [
        OrganizationIdentifier(type="ror", value="002t25c44"),
        OrganizationIdentifier(type="wikidata", value="Q12345"),
    ]
    monkeypatch.setattr(
        organization_factory.OrganizationFactory,
        "solve_identifier",
        # the solver must return the new seen types along with the provided seen
        AsyncMock(
            return_value=(
                deref_identifiers,
                [
                    "idref",
                    "hal",
                    "ror",
                    "wikidata",
                ],
            )
        ),
    )

    solver = IdrefOrganizationSolver(timeout=1)
    identifiers, seen = await solver.solve_identifier(
        OrganizationInformations(
            name="Université Paris 1 Panthéon-Sorbonne",
            identifier="scanr_idref_027361802",
            source="scanr",
        ),
        seen=[],
    )

    received_identifiers = {(i.type, i.value) for i in identifiers}

    # base
    assert ("idref", "027361802") in received_identifiers

    # saved identifiers (from sameAs)
    assert ("hal", "7550") in received_identifiers
    assert ("isni", "000000012173743X") in received_identifiers
    assert ("viaf", "143080305") in received_identifiers

    # deref merged
    assert ("ror", "002t25c44") in received_identifiers
    assert ("wikidata", "Q12345") in received_identifiers

    # sanity on seen
    assert "idref" in seen
    assert "ror" in seen  # after deref
    assert "hal" in seen
    assert "isni" in seen
    assert "viaf" in seen


@pytest.mark.asyncio
async def test_idref_solver_ror_deref_failure_falls_back_to_raw_ror(
    monkeypatch, idref_rdf_xml_minimal
):
    """
    GIVEN IdRef RDF contains sameAs ROR
    WHEN deep deref fails
    THEN we still store OrganizationIdentifier(type='ror', value='002t25c44') via fallback.
    """
    response = _FakeResponse(status=200, text_payload=idref_rdf_xml_minimal)
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

    solver = IdrefOrganizationSolver(timeout=1)
    identifiers, _ = await solver.solve_identifier(
        OrganizationInformations(
            name="Université Paris 1 Panthéon-Sorbonne",
            identifier="scanr_idref_027361802",
            source="scanr",
        ),
        seen=[],
    )

    received_identifiers = {(i.type, i.value) for i in identifiers}
    assert ("ror", "002t25c44") in received_identifiers


@pytest.mark.asyncio
async def test_idref_solver_non_2xx_raises(monkeypatch):
    """
    GIVEN IdRef endpoint returns non-2xx
    WHEN solve_identifier() is called
    THEN it raises DereferencingError
    """
    response = _FakeResponse(status=404, text_payload="nope")
    fake_session = _FakeSession(response)

    from app.http.aio_http_client_manager import AioHttpClientManager

    monkeypatch.setattr(
        AioHttpClientManager, "get_session", AsyncMock(return_value=fake_session)
    )

    solver = IdrefOrganizationSolver(timeout=1)

    with pytest.raises(DereferencingError):
        await solver.solve_identifier(
            OrganizationInformations(
                name="Université Paris 1 Panthéon-Sorbonne",
                identifier="scanr_idref_027361802",
                source="scanr",
            ),
            seen=[],
        )


@pytest.mark.asyncio
async def test_idref_solve_builds_organization_and_attaches_identifiers(
    monkeypatch, idref_rdf_xml_minimal
):
    """
    GIVEN solve() is called with OrganizationInformations (name/source/identifier)
    WHEN solve() runs
    THEN it returns an Organization with same source/source_identifier/name and identifiers attached.
    """
    response = _FakeResponse(status=200, text_payload=idref_rdf_xml_minimal)
    fake_session = _FakeSession(response)

    from app.http.aio_http_client_manager import AioHttpClientManager

    monkeypatch.setattr(
        AioHttpClientManager, "get_session", AsyncMock(return_value=fake_session)
    )

    from app.services.organizations import organization_factory

    monkeypatch.setattr(
        organization_factory.OrganizationFactory,
        "solve_identifier",
        AsyncMock(return_value=([], ["idref"])),
    )

    solver = IdrefOrganizationSolver(timeout=1)
    org = await solver.solve(
        OrganizationInformations(
            name="Université Paris 1 Panthéon-Sorbonne",
            identifier="scanr_idref_027361802",
            source="scanr",
        )
    )

    assert org.source == "scanr"
    assert org.source_identifier == "scanr_idref_027361802"
    assert org.name == "Université Paris 1 Panthéon-Sorbonne"
    assert len(org.identifiers) >= 1
    assert any(i.type == "idref" and i.value == "027361802" for i in org.identifiers)
