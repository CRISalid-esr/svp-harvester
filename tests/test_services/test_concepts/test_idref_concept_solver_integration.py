from datetime import datetime, timedelta
from unittest import mock

import aiosparql.client
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.references.references_recorder import ReferencesRecorder
from app.harvesters.idref.idref_harvester import IdrefHarvester
from app.harvesters.idref.idref_references_converter import IdrefReferencesConverter
from app.models.references import Reference


@pytest.fixture(name="idref_sparql_endpoint_client_mock_with_test_concept")
def fixture_idref_sparql_endpoint_client_mock_with_test_concept(
    idref_sparql_endpoint_results_with_test_concept: dict,
):
    """Retrieval service mock to detect run method calls."""
    with mock.patch.object(
        aiosparql.client.SPARQLClient, "query"
    ) as aiosparql_client_query:
        aiosparql_client_query.return_value = (
            idref_sparql_endpoint_results_with_test_concept
        )
        yield aiosparql_client_query


@pytest.mark.asyncio
async def test_idref_harvester_gets_concept_resolved(
    harvesting_db_model_for_person_with_idref,
    idref_sparql_endpoint_client_mock_with_test_concept,  # pylint: disable=unused-argument
    async_session: AsyncSession,
):
    """
    Given data containing a concept returned by the Idref SPARQL endpoint
    When the harvester is run
    Then the concept is resolved

    :param harvesting_db_model_for_person_with_idref:
    :param idref_sparql_endpoint_client_mock_with_test_concept:
    :param async_session:
    :return:
    """
    with mock.patch.object(
        ReferencesRecorder, "register_creation"
    ) as reference_recorder_register_mock:
        harvester = IdrefHarvester(converter=IdrefReferencesConverter())
        async_session.add(harvesting_db_model_for_person_with_idref)
        await async_session.commit()
        harvester.set_harvesting_id(harvesting_db_model_for_person_with_idref.id)
        harvester.set_entity_id(
            harvesting_db_model_for_person_with_idref.retrieval.entity_id
        )
        await harvester.run()
        _, arg = reference_recorder_register_mock.call_args
        reference: Reference = arg["new_ref"]

        assert len(reference.subjects) == 1
        concept = reference.subjects[0]
        assert concept.uri == "http://www.idref.fr/allowed_concept_for_tests/id"
        assert len(concept.labels) == 4
        assert any(
            label.value == "Concept Idref autorisé pour les tests"
            for label in concept.labels
            if label.language == "fr" and label.preferred
        )
        assert any(
            label.value == "Idref concept allowed for test"
            for label in concept.labels
            if label.language == "en" and label.preferred
        )
        assert any(
            label.value == "Concept Idref que vous pouvez utiliser pour les tests"
            for label in concept.labels
            if label.language == "fr" and not label.preferred
        )
        assert any(
            label.value == "Idref concept you can use for tests"
            for label in concept.labels
            if label.language == "en" and not label.preferred
        )
        assert concept.dereferenced
        # data time is not older than one minute
        assert concept.last_dereferencing_date_time > (
            datetime.now() - timedelta(minutes=1)
        )
