"""Tests for the Person model."""

import urllib
from unittest import mock

import aiohttp
import pytest
from semver import VersionInfo
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.models.concept import Concept
from app.db.models.document_type import DocumentType
from app.db.models.harvesting import Harvesting
from app.db.models.label import Label
from app.db.models.person import Person as DbPerson
from app.db.models.reference import Reference
from app.db.models.reference_event import ReferenceEvent
from app.db.references.references_recorder import ReferencesRecorder
from app.harvesters.hal.hal_harvester import HalHarvester
from app.harvesters.hal.hal_references_converter import HalReferencesConverter


@pytest.fixture(name="hal_api_client_mock")
def fixture_hal_api_client_mock(hal_api_docs_for_researcher: dict):
    """Retrieval service mock to detect run method calls."""
    with mock.patch.object(aiohttp.ClientSession, "get") as aiohttp_client_session_get:
        aiohttp_client_session_get.return_value.__aenter__.return_value.status = 200
        aiohttp_client_session_get.return_value.__aenter__.return_value.json.return_value = (
            hal_api_docs_for_researcher
        )
        yield aiohttp_client_session_get


@pytest.fixture(name="hal_api_client_mock_same_kw_twice")
def fixture_hal_api_client_mock_same_kw_twice(hal_api_docs_with_same_kw_twice: dict):
    """Retrieval service mock to detect run method calls."""
    with mock.patch.object(aiohttp.ClientSession, "get") as aiohttp_client_session_get:
        aiohttp_client_session_get.return_value.__aenter__.return_value.status = 200
        aiohttp_client_session_get.return_value.__aenter__.return_value.json.return_value = (
            hal_api_docs_with_same_kw_twice
        )

        yield aiohttp_client_session_get


@pytest.fixture(name="reference_recorder_register_mock")
def fixture_reference_recorder_register_mock():
    """Reference recorder mock to detect register method calls."""
    with mock.patch.object(
        ReferencesRecorder, "register_creation"
    ) as reference_recorder_register_mock:
        yield reference_recorder_register_mock


@pytest.fixture(name="hal_harvester")
def fixture_hal_harvester() -> HalHarvester:
    """Fixture for a HalHarvester instance."""
    converter = HalReferencesConverter()
    return HalHarvester(converter=converter)


def test_hal_harvester_relevant_for_person_with_idhal_i(
    person_with_name_and_id_hal_i_db_model: DbPerson,
    hal_harvester: HalHarvester,
):
    """Test that the harvester will run if submitted with an IDHAL."""
    assert hal_harvester.is_relevant(person_with_name_and_id_hal_i_db_model) is True


def test_hal_harvester_relevant_for_person_with_idhal_s(
    person_with_name_and_id_hal_s_db_model: DbPerson,
    hal_harvester: HalHarvester,
):
    """Test that the harvester will run if submitted with an IDHAL."""
    assert hal_harvester.is_relevant(person_with_name_and_id_hal_s_db_model) is True


def test_hal_harvester_relevant_for_person_with_orcid(
    person_with_name_and_orcid_db_model: DbPerson,
    hal_harvester: HalHarvester,
):
    """Test that the harvester will run if submitted with an ORCID."""
    assert hal_harvester.is_relevant(person_with_name_and_orcid_db_model) is True


def test_hal_harvester_not_relevant_for_person_with_idref_only(
    person_with_name_and_idref_db_model: DbPerson,
    hal_harvester: HalHarvester,
):
    """Test that the harvester will not run if submitted with only an IDREF."""
    assert hal_harvester.is_relevant(person_with_name_and_idref_db_model) is False


@pytest.mark.integration
@pytest.mark.asyncio
async def test_hal_harvester_finds_doc(
    hal_harvester: HalHarvester,
    hal_harvesting_db_model_id_hal_i,
    reference_recorder_register_mock,
    hal_api_client_mock,
    async_session: AsyncSession,
):
    """Test that the harvester will find documents."""
    async_session.add(hal_harvesting_db_model_id_hal_i)
    await async_session.commit()
    hal_harvester.set_harvesting_id(hal_harvesting_db_model_id_hal_i.id)
    hal_harvester.set_entity_id(hal_harvesting_db_model_id_hal_i.retrieval.entity_id)
    await hal_harvester.run()
    hal_api_client_mock.assert_called_once()
    reference_recorder_register_mock.assert_called_once()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_hal_harvester_calls_hal_api_with_id_hal_s(
    hal_harvester: HalHarvester,
    hal_harvesting_db_model_id_hal_s: Harvesting,
    hal_api_client_mock,
    async_session: AsyncSession,
):
    """
    Given a person in db model format with an id_hal_s
    When it is submitted to the harvester and the harvester is run
    Then Hal API client is called with a query with id_hal_s as search criteria

    :param hal_harvester:
    :param hal_harvesting_db_model_id_hal_s:
    :param hal_api_client_mock:
    :param async_session:
    :return:
    """
    async_session.add(hal_harvesting_db_model_id_hal_s)
    await async_session.commit()
    hal_harvester.set_harvesting_id(hal_harvesting_db_model_id_hal_s.id)
    hal_harvester.set_entity_id(hal_harvesting_db_model_id_hal_s.retrieval.entity_id)
    await hal_harvester.run()
    hal_api_client_mock.assert_called_once()
    args, _ = hal_api_client_mock.call_args
    query = urllib.parse.urlsplit(args[0]).query
    # Split the query into a dict
    query_dict = dict(urllib.parse.parse_qsl(query))
    # Check that the query contains the id_hal_s as 'q' parameter
    id_hal_s = hal_harvesting_db_model_id_hal_s.retrieval.entity.get_identifier(
        "id_hal_s"
    )
    assert query_dict["q"] == f"authIdHal_s:{id_hal_s}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_hal_harvester_calls_hal_api_with_id_hal_i_s(
    hal_harvester: HalHarvester,
    hal_harvesting_db_model_id_hal_i_s: Harvesting,
    hal_api_client_mock,
    async_session: AsyncSession,
):
    """
    Given a person in db model format with both an id_hal_i and an id_hal_s
    When it is submitted to the harvester and the harvester is run
    Then Hal API client is called with a query with id_hal_i as search criteria

    :param hal_harvester:
    :param hal_harvesting_db_model_id_hal_i_s:
    :param hal_api_client_mock:
    :param async_session:
    :return:
    """
    async_session.add(hal_harvesting_db_model_id_hal_i_s)
    await async_session.commit()
    hal_harvester.set_harvesting_id(hal_harvesting_db_model_id_hal_i_s.id)
    hal_harvester.set_entity_id(hal_harvesting_db_model_id_hal_i_s.retrieval.entity_id)
    await hal_harvester.run()
    hal_api_client_mock.assert_called_once()
    args, _ = hal_api_client_mock.call_args
    query = urllib.parse.urlsplit(args[0]).query
    # Split the query into a dict
    query_dict = dict(urllib.parse.parse_qsl(query))
    # Check that the query contains the id_hal_i as 'q' parameter
    id_hal_i = hal_harvesting_db_model_id_hal_i_s.retrieval.entity.get_identifier(
        "id_hal_i"
    )
    assert query_dict["q"] == f"authIdHal_i:{id_hal_i}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_hal_harvester_registers_docs_in_db(
    hal_harvester: HalHarvester,
    hal_harvesting_db_model_id_hal_i,
    hal_api_client_mock,
    hal_api_docs_for_researcher: dict,
    async_session: AsyncSession,
):
    """Test that after harvesting, the references are registered in the database."""
    async_session.add(hal_harvesting_db_model_id_hal_i)
    await async_session.commit()
    hal_harvester.set_harvesting_id(hal_harvesting_db_model_id_hal_i.id)
    hal_harvester.set_entity_id(hal_harvesting_db_model_id_hal_i.retrieval.entity_id)
    await hal_harvester.run()
    hal_api_client_mock.assert_called_once()
    stmt = (
        select(Reference, ReferenceEvent)
        .join(ReferenceEvent)
        .join(Harvesting)
        .filter(Harvesting.id == hal_harvesting_db_model_id_hal_i.id)
    )
    result = (await async_session.execute(stmt)).unique()
    results = list(result)
    assert len(results) == 1
    reference = results[0][0]
    reference_event = results[0][1]
    assert (
        reference.titles[0].value
        == hal_api_docs_for_researcher.get("response")
        .get("docs")[0]
        .get("en_title_s")[0]
    )
    assert reference.source_identifier == hal_api_docs_for_researcher.get(
        "response"
    ).get("docs")[0].get("halId_s")
    assert reference_event.type == ReferenceEvent.Type.CREATED.value


@pytest.mark.integration
@pytest.mark.asyncio
async def test_hal_harvester_registers_one_kw_for_two_occurences(
    hal_harvester: HalHarvester,
    hal_harvesting_db_model_id_hal_i,
    hal_api_client_mock_same_kw_twice,
    async_session: AsyncSession,
):
    """
    The first publication has a concept,
    and the same concept is mentioned twice in a later publication.
    """
    async_session.add(hal_harvesting_db_model_id_hal_i)
    await async_session.commit()
    hal_harvester.set_harvesting_id(hal_harvesting_db_model_id_hal_i.id)
    hal_harvester.set_entity_id(hal_harvesting_db_model_id_hal_i.retrieval.entity_id)
    await hal_harvester.run()
    hal_api_client_mock_same_kw_twice.assert_called_once()
    stmt = (
        select(Reference)
        .options(joinedload(Reference.subjects).joinedload(Concept.labels))
        .join(Concept, Reference.subjects)
        .join(Label, Concept.labels)
        .join(ReferenceEvent)
        .join(Harvesting)
        .filter(Harvesting.id == hal_harvesting_db_model_id_hal_i.id)
    )
    result = (await async_session.execute(stmt)).unique().scalars()
    results = list(result)
    # the result with doc_id 1299757 has only one concept
    assert len(results) == 2
    first_result = [r for r in results if r.source_identifier == "hal-01299757"][0]
    second_result = [r for r in results if r.source_identifier == "hal-01416567"][0]
    assert len(first_result.subjects) == 1
    assert len(second_result.subjects) == 2
    assert any(
        first_result.subjects[0].labels[0].value == concept.labels[0].value
        for concept in second_result.subjects
    )
    assert any(
        concept.labels[0].value == "International trade"
        for concept in second_result.subjects
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_hal_harvester_registers_abstract(
    hal_harvester: HalHarvester,
    hal_harvesting_db_model_id_hal_i,
    hal_api_client_mock,  # pylint: disable=unused-argument
    async_session: AsyncSession,
):
    """
    GIVEN a hal response with a value in "en_abstract_s" field
    WHEN the harvester is run
    THEN the abstract is registered in reference abstracts field with "en" as language

    :param hal_harvester:
    :param hal_harvesting_db_model_id_hal_i:
    :param hal_api_client_mock:
    :param async_session:
    :return:
    """
    async_session.add(hal_harvesting_db_model_id_hal_i)
    await async_session.commit()
    hal_harvester.set_harvesting_id(hal_harvesting_db_model_id_hal_i.id)
    hal_harvester.set_entity_id(hal_harvesting_db_model_id_hal_i.retrieval.entity_id)
    await hal_harvester.run()
    stmt = (
        select(Reference)
        .options(joinedload(Reference.abstracts))
        .join(ReferenceEvent)
        .join(Harvesting)
        .filter(Harvesting.id == hal_harvesting_db_model_id_hal_i.id)
    )
    result = (await async_session.execute(stmt)).unique().scalar_one_or_none()
    assert result is not None
    assert len(result.abstracts) == 1
    assert result.abstracts[0].value == "This article focuses on Vernant..."
    assert result.abstracts[0].language == "en"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_hal_harvester_register_document_type_in_db(
    hal_harvester: HalHarvester,
    hal_harvesting_db_model_id_hal_i,
    hal_api_client_mock,
    async_session: AsyncSession,
):
    """Test that after harvesting, the document type are registered in the database."""
    async_session.add(hal_harvesting_db_model_id_hal_i)
    await async_session.commit()
    hal_harvester.set_harvesting_id(hal_harvesting_db_model_id_hal_i.id)
    hal_harvester.set_entity_id(hal_harvesting_db_model_id_hal_i.retrieval.entity_id)
    await hal_harvester.run()
    hal_api_client_mock.assert_called_once()
    stmt = select(DocumentType.uri)
    result = await async_session.execute(stmt)
    results = list(result)
    assert len(results) == 1


@pytest.mark.asyncio
async def test_harvester_version_number_increased(
    hal_harvester: HalHarvester,
    hal_harvesting_db_model_id_hal_i,
    hal_api_client_mock,
    hal_api_docs_for_researcher: dict,
    async_session: AsyncSession,
):
    """
    Test that if we harvest the same data twice, with increased harvester vesion number,
    a reference event of type unchanged is created, its flag enhanced is set to True
    and a new version of the reference is created

    :param hal_harvester:
    :param hal_harvesting_db_model_id_hal_i:
    :param hal_api_client_mock:
    :param hal_api_docs_for_researcher:
    :param async_session:
    :return:
    """
    with mock.patch.object(HalHarvester, "get_version") as hal_harvester_version:
        hal_harvester_version.return_value = VersionInfo.parse("1.0.0")
        async_session.add(hal_harvesting_db_model_id_hal_i)
        await async_session.commit()
        hal_harvester.set_harvesting_id(hal_harvesting_db_model_id_hal_i.id)
        hal_harvester.set_entity_id(
            hal_harvesting_db_model_id_hal_i.retrieval.entity_id
        )
        await hal_harvester.run()
        hal_api_client_mock.assert_called_once()
        stmt = (
            select(Reference, ReferenceEvent)
            .join(ReferenceEvent)
            .join(Harvesting)
            .filter(Harvesting.id == hal_harvesting_db_model_id_hal_i.id)
        )
        result = (await async_session.execute(stmt)).unique()
        results = list(result)
        assert len(results) == 1
        reference1 = results[0][0]
        reference_event = results[0][1]
        assert reference_event.type == ReferenceEvent.Type.CREATED.value
        hal_harvester_version.return_value = VersionInfo.parse("1.0.1")
        await hal_harvester.run()
        stmt = (
            select(Reference, ReferenceEvent)
            .join(ReferenceEvent)
            .join(Harvesting)
            .filter(Harvesting.id == hal_harvesting_db_model_id_hal_i.id)
        )
        result = (await async_session.execute(stmt)).unique()
        results = list(result)
        assert len(results) == 2
        # reorder results by reference event id
        if results[0][1].id > results[1][1].id:
            results = [results[1], results[0]]
        reference2 = results[1][0]
        reference_event = results[1][1]
        assert reference_event.type == ReferenceEvent.Type.UNCHANGED.value
        assert reference_event.enhanced is True
        assert reference2.version == reference1.version + 1
        assert reference2.titles[0].value == reference1.titles[0].value
