"""Tests for the Person model."""
import pickle
from unittest import mock

import aiosparql
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_app_settings
from app.db.models.reference import Reference
from app.db.references.references_recorder import ReferencesRecorder
from app.harvesters.idref.idref_harvester import IdrefHarvester
from app.harvesters.idref.idref_references_converter import IdrefReferencesConverter
from app.services.cache.third_api_cache import ThirdApiCache


@pytest.fixture(name="idref_sparql_endpoint_client_mock_with_sudoc_cached_pub")
def fixture_idref_sparql_endpoint_client_mock_with_sudoc_cached(
    idref_sparql_endpoint_results_with_sudoc_cached_pub: dict,
):
    """Retrieval service mock to detect run method calls."""
    with mock.patch.object(
        aiosparql.client.SPARQLClient, "query"
    ) as aiosparql_client_query:
        aiosparql_client_query.return_value = (
            idref_sparql_endpoint_results_with_sudoc_cached_pub
        )
        yield aiosparql_client_query


@pytest.fixture(name="idref_sparql_endpoint_client_mock_with_sudoc_not_cached_pub")
def fixture_idref_sparql_endpoint_client_mock_with_sudoc_not_cached_pub(
    idref_sparql_endpoint_results_with_sudoc_pub: dict,
):
    """Retrieval service mock to detect run method calls."""
    with mock.patch.object(
        aiosparql.client.SPARQLClient, "query"
    ) as aiosparql_client_query:
        aiosparql_client_query.return_value = (
            idref_sparql_endpoint_results_with_sudoc_pub
        )
        yield aiosparql_client_query


async def test_third_party_cache():
    """
    Test that ThirdApiCache returns a rdflib graph
    """

    cache = ThirdApiCache()
    value = await cache.get(
        api_name="sudoc_publications", key="https://www.sudoc.fr/070266875.rdf"
    )
    assert value is not None
    assert len(list(value.subjects())) == 57


@pytest.fixture(name="reference_recorder_register_mock")
def fixture_reference_recorder_register_mock():
    """Reference recorder mock to detect register method calls."""
    with mock.patch.object(
        ReferencesRecorder, "register_creation"
    ) as reference_recorder_register_mock:
        yield reference_recorder_register_mock


@pytest.mark.asyncio
async def test_idref_harvester_takes_sudoc_doc_from_cache(
    harvesting_db_model_for_person_with_idref,
    reference_recorder_register_mock,
    rdf_resolver_mock,  # pylint: disable=unused-argument
    idref_sparql_endpoint_client_mock_with_sudoc_cached_pub,  # pylint: disable=unused-argument
    async_session: AsyncSession,
):
    """
    GIVEN an Idref harvester that finds a sudoc publication whose URI is in cache
    WHEN the harvester runs
    THEN the Sudoc RDF endpoint is not called

    :param harvesting_db_model_for_person_with_idref:
    :param reference_recorder_register_mock:
    :param idref_sparql_endpoint_client_mock_with_sudoc_cached_pub:
    :param async_session:
    :return:
    """
    settings = get_app_settings()
    settings.third_api_caching_enabled = True

    harvester = IdrefHarvester(converter=IdrefReferencesConverter())
    async_session.add(harvesting_db_model_for_person_with_idref)
    await async_session.commit()
    harvester.set_harvesting_id(harvesting_db_model_for_person_with_idref.id)
    harvester.set_entity_id(
        harvesting_db_model_for_person_with_idref.retrieval.entity_id
    )
    await harvester.run()
    idref_sparql_endpoint_client_mock_with_sudoc_cached_pub.assert_called_once()
    rdf_resolver_mock.assert_not_called()
    reference_recorder_register_mock.assert_called_once()
    _, arg = reference_recorder_register_mock.call_args
    reference: Reference = arg["new_ref"]
    assert len(reference.titles) == 1
    assert (
        reference.titles[0].value
        == 'Les Cahiers du Rhône dans la guerre (1941-1945)  : la Résistance du "Glaive de l\'Esprit"'
    )


@pytest.mark.asyncio
async def test_idref_harvester_puts_sudoc_reponse_in_cache(
    harvesting_db_model_for_person_with_idref,
    reference_recorder_register_mock,
    rdf_resolver_mock,  # pylint: disable=unused-argument
    redis_cache_mock,  # pylint: disable=unused-argument
    idref_sparql_endpoint_client_mock_with_sudoc_not_cached_pub,  # pylint: disable=unused-argument
    async_session: AsyncSession,
):
    """
    GIVEN an Idref harvester that finds a sudoc publication whose URI is not in cache
    WHEN the harvester runs
    THEN the get method of ThirdApiCache is called and returns None,
    the Sudoc RDF endpoint is called and returns a graph,
    the set method of ThirdApiCache is called with the URI and the graph

    :param harvesting_db_model_for_person_with_idref:
    :param reference_recorder_register_mock:
    :param rdf_resolver_mock:
    :param redis_cache_mock:
    :param idref_sparql_endpoint_client_mock_with_sudoc_not_cached_pub:
    :param async_session:
    :return:
    """

    settings = get_app_settings()
    settings.third_api_caching_enabled = True

    harvester = IdrefHarvester(converter=IdrefReferencesConverter())
    async_session.add(harvesting_db_model_for_person_with_idref)
    await async_session.commit()
    harvester.set_harvesting_id(harvesting_db_model_for_person_with_idref.id)
    harvester.set_entity_id(
        harvesting_db_model_for_person_with_idref.retrieval.entity_id
    )
    await harvester.run()
    idref_sparql_endpoint_client_mock_with_sudoc_not_cached_pub.assert_called_once()
    rdf_resolver_mock.assert_called_once()
    reference_recorder_register_mock.assert_called_once()
    redis_cache_get, redis_cache_set = redis_cache_mock
    redis_cache_get.assert_called_once()
    redis_cache_set.assert_called_once()
    _, arg = redis_cache_set.call_args
    assert arg["name"] == "sudoc_publications:https://www.sudoc.fr/193726130.rdf"
    cached_value = arg["value"]
    graph_from_cache = pickle.loads(cached_value)
    assert len(list(graph_from_cache.subjects())) == 60
    _, arg = reference_recorder_register_mock.call_args
    reference: Reference = arg["new_ref"]
    assert len(reference.titles) == 2
    assert (
        reference.titles[0].value
        == "Agriculture des métropoles  : voie d'avenir ou cache-misère ?"
    )
