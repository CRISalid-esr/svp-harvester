from unittest import mock

import aiohttp
import pytest

from app.db.models.concept import Concept as DbConcept
from app.services.concepts.idref_concept_solver import IdRefConceptSolver


@pytest.fixture(name="idref_http_client_mock")
def fixture_idref_http_client_mock(idref_rdf_raw_result_for_concept: str):
    """Retrieval service mock to detect run method calls."""
    with mock.patch.object(aiohttp.ClientSession, "get") as aiohttp_client_session_get:
        aiohttp_client_session_get.return_value.__aenter__.return_value.status = 200
        aiohttp_client_session_get.return_value.__aenter__.return_value.text.return_value = (
            idref_rdf_raw_result_for_concept
        )
        yield aiohttp_client_session_get


@pytest.mark.asyncio
async def test_idref_conscept_solver_calls_url_from_uri():
    """
    GIVEN an idref concept solver
    WHEN calling it with the concept id https://www.idref.fr/082303363/id
    THEN the URL https://www.idref.fr/082303363.rdf is called through aiohttp
    :return:
    """
    concept_id = "https://www.idref.fr/082303363/id"
    with mock.patch("aiohttp.ClientSession.get") as mock_get:
        await IdRefConceptSolver().solve(concept_id=concept_id)
        mock_get.assert_called_once_with("https://www.idref.fr/082303363.rdf")


@pytest.mark.asyncio
async def test_idref_conscept_solver_calls_url_from_numeric_id():
    """
    GIVEN an idref concept solver
    WHEN calling it with the concept id "082303363"
    THEN the URL https://www.idref.fr/082303363.rdf is called through aiohttp
    :return:
    """
    concept_id = "082303363"
    with mock.patch("aiohttp.ClientSession.get") as mock_get:
        await IdRefConceptSolver().solve(concept_id=concept_id)
        mock_get.assert_called_once_with("https://www.idref.fr/082303363.rdf")


@pytest.mark.asyncio
async def test_idref_conscept_solver_raises_value_error_with_fantasy_string():
    """
    GIVEN an idref concept solver
    WHEN calling it with the concept id "fantasy"
    THEN a Value error is raised with the message "Invalid idref concept id or uri {concept_id}"
    and the aiohttp client is not called
    :return:
    """
    concept_id = "fantasy"
    with mock.patch("aiohttp.ClientSession.get") as mock_get:
        with pytest.raises(ValueError) as exception_info:
            await IdRefConceptSolver().solve(concept_id=concept_id)
        assert (
            exception_info.value.args[0]
            == f"Invalid idref concept id or uri {concept_id}"
        )
        mock_get.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.current
async def test_idref_concept_solver_returns_db_concept(idref_http_client_mock):
    """
    GIVEN an idref concept solver
    WHEN calling it with the concept id "082303363"
    THEN the returned value is a DbConcept with the correct uri and label
    :return:
    """
    concept_id = "082303363"
    result = await IdRefConceptSolver().solve(concept_id=concept_id)
    idref_http_client_mock.assert_called_once_with("https://www.idref.fr/082303363.rdf")
    assert result is not None
    assert isinstance(result, DbConcept)
    assert result.uri == "http://www.idref.fr/082303363/id"
    assert "Bouillabaisse" in [
        label.value
        for label in result.labels
        if label.language == "fr" and label.preferred
    ]
