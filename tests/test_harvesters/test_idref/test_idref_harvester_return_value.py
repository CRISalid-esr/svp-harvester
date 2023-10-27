from unittest import mock

import aiosparql.client
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.harvesters.idref.idref_harvester import IdrefHarvester
from app.harvesters.idref.idref_references_converter import IdrefReferencesConverter
from app.models.references import Reference


@pytest.fixture(name="idref_sparql_endpoint_client_mock")
def fixture_idref_sparql_endpoint_client_mock(
    idref_sparql_endpoint_results_with_one_idref_pub: dict,
):
    """Retrieval service mock to detect run method calls."""
    with mock.patch.object(
        aiosparql.client.SPARQLClient, "query"
    ) as aiosparql_client_query:
        aiosparql_client_query.return_value = (
            idref_sparql_endpoint_results_with_one_idref_pub
        )
        yield aiosparql_client_query


@pytest.mark.current
@pytest.mark.integration
@pytest.mark.asyncio
async def test_idref_harvester_finds_doc(
    harvesting_db_model_for_person_with_idref,
    reference_recorder_register_mock,
    idref_sparql_endpoint_client_mock,
    async_session: AsyncSession,
):
    """Test that the harvester will find documents."""
    harvester = IdrefHarvester(converter=IdrefReferencesConverter())
    async_session.add(harvesting_db_model_for_person_with_idref)
    await async_session.commit()
    harvester.set_harvesting_id(harvesting_db_model_for_person_with_idref.id)
    harvester.set_entity_id(
        harvesting_db_model_for_person_with_idref.retrieval.entity_id
    )
    await harvester.run()
    idref_sparql_endpoint_client_mock.assert_called_once()
    reference_recorder_register_mock.assert_called_once()
    _, arg = reference_recorder_register_mock.call_args
    reference: Reference = arg["new_ref"]
    assert len(reference.titles) == 1
    assert (
        reference.titles[0].value
        == "Ressources mondialisées, Essais de géographie politique"
    )
    assert reference.titles[0].language == "fr"
    assert len(reference.abstracts) == 1
    assert (
        reference.abstracts[0].value
        == "La société 2.0 qui fait l'air du temps mondialisé ne se réduit pas "
        "à l'information numérique et aux flux immatériels."
    )
    assert len(reference.subjects) == 3
    assert any(
        subject.uri == "http://www.idref.fr/027732428/id"
        and any(
            label.language == "fr" and label.value == "Géopolitique"
            for label in subject.labels
        )
        for subject in reference.subjects
    )
