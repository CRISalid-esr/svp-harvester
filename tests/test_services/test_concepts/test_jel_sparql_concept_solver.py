from unittest import mock

import aiohttp
import aiosparql
import pytest

from app.config import get_app_settings
from app.db.models.concept import Concept as DbConcept
from app.services.concepts.idref_concept_solver import IdRefConceptSolver
from app.services.concepts.sparql_jel_concept_solver import SparqlJelConceptSolver


@pytest.fixture(name="mock_sparql_jel_concept_solver", autouse=True)
def fixture_mock_sparql_jel_concept_solver():
    """Disable mock for SparqlJelConceptSolver."""
    return


@pytest.fixture(name="jel_sparql_endpoint_client_mock_with_concept")
def fixture_jel_sparql_endpoint_client_mock_with_concept(
    jel_sparql_endpoint_response_for_concept: dict,
):
    """Retrieval service mock to detect run method calls."""
    with mock.patch.object(
        aiosparql.client.SPARQLClient, "query"
    ) as aiosparql_client_query:
        aiosparql_client_query.return_value = jel_sparql_endpoint_response_for_concept
        yield aiosparql_client_query


@pytest.mark.asyncio
@pytest.mark.current
async def test_jel_sparql_concept_solver_returns_db_concept(
    jel_sparql_endpoint_client_mock_with_concept,
):
    """
    GIVEN the jel idref concept solver
    WHEN calling it with the concept id "G2"
    THEN the returned value is a DbConcept with the correct uri and label
    :return:
    """
    concept_id = "G2"
    solver = SparqlJelConceptSolver()
    concept_uri = solver.get_uri(concept_id)
    result = await solver.solve(concept_id=concept_uri)
    jel_sparql_endpoint_client_mock_with_concept.assert_called_once()
    args, _ = jel_sparql_endpoint_client_mock_with_concept.call_args
    assert "SELECT ?prefLabel ?altLabel" in args[0]
    assert concept_uri in args[0]
    assert result is not None
    assert isinstance(result, DbConcept)
    assert result.uri == "http://zbw.eu/beta/external_identifiers/jel#G2"
    assert "B - History of Economic Thought, Methodology, and Heterodox Approaches" in [
        label.value
        for label in result.labels
        if label.language == "en" and label.preferred
    ]
