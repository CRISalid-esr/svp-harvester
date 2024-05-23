from unittest import mock

import aiohttp
import pytest

from app.db.models.concept import Concept as DbConcept
from app.services.concepts.abes_concept_solver import AbesConceptSolver
from app.services.concepts.concept_informations import ConceptInformations


@pytest.fixture(name="mock_abes_concept_solver", autouse=True)
def fixture_mock_abes_concept_solver():
    """Disable mock for AbesConceptSolver."""
    return


@pytest.fixture(name="abes_concept_http_client_mock")
def fixture_abes_concept_http_client_mock(science_plus_raw_result_for_concept: str):
    """Retrieval service mock to detect run method calls."""
    with mock.patch.object(aiohttp.ClientSession, "get") as aiohttp_client_session_get:
        aiohttp_client_session_get.return_value.__aenter__.return_value.status = 200
        aiohttp_client_session_get.return_value.__aenter__.return_value.text.return_value = (
            science_plus_raw_result_for_concept
        )
        yield aiohttp_client_session_get


@pytest.mark.asyncio
async def test_abes_concept_solver_returns_db_concept(abes_concept_http_client_mock):
    """
    GIVEN an abes concept solver
    WHEN calling it with the concept id
     "http://hub.abes.fr/cairn/periodical/autr/2008/issue_autr045/D33AF39D3B7834E0E053120B220A2036/subject/environment"
    THEN the returned value is a DbConcept with the correct uri and label
    :return:
    """
    concept_id = "http://hub.abes.fr/cairn/periodical/autr/2008/issue_autr045/D33AF39D3B7834E0E053120B220A2036/subject/environment"
    concept_informations = ConceptInformations(uri=concept_id)
    solver = AbesConceptSolver()
    solver.complete_information(concept_informations)
    result = await solver.solve(concept_informations)
    abes_concept_http_client_mock.assert_called_once_with(
        "https://scienceplus.abes.fr/sparql?query=define%20sql%3Adescribe-mode%20%22CBD%22%20%20DESCRIBE%20%3C"
        "http%3A//hub.abes.fr/cairn/periodical/autr/2008/issue_autr045/D33AF39D3B7834E0E053120B220A2036/subject/environment"
        "%3E&output=application%2Frdf%2Bxml"
    )

    assert result is not None
    assert isinstance(result, DbConcept)
    assert result.uri == concept_id
    assert "environment" in [
        label.value
        for label in result.labels
        if label.language == "en" and label.preferred
    ]
