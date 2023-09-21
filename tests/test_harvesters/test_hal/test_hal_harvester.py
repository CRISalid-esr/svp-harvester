"""Tests for the Person model."""
from unittest import mock

import aiohttp
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_app_settings
from app.db.models import Reference, ReferenceEvent, Harvesting
from app.db.references.references_recorder import ReferencesRecorder
from app.harvesters.hal.hal_harvester import HalHarvester
from app.harvesters.hal.hal_references_converter import HalReferencesConverter
from app.models.people import Person


@pytest.fixture(name="hal_api_client_mock")
def fixture_hal_api_client_mock(hal_api_docs_for_one_researcher: dict):
    """Retrieval service mock to detect run method calls."""
    with mock.patch.object(aiohttp.ClientSession, "get") as aiohttp_client_session_get:
        aiohttp_client_session_get.return_value.__aenter__.return_value.status = 200
        aiohttp_client_session_get.return_value.__aenter__.return_value.json.return_value \
            = hal_api_docs_for_one_researcher

        yield aiohttp_client_session_get


@pytest.fixture(name="reference_recorder_register_mock")
def fixture_reference_recorder_register_mock():
    """Reference recorder mock to detect register method calls."""
    with mock.patch.object(ReferencesRecorder, "register") as reference_recorder_register_mock:
        yield reference_recorder_register_mock


@pytest.fixture(name="hal_harvester")
def fixture_hal_harvester() -> HalHarvester:
    """Fixture for a HalHarvester instance."""
    converter = HalReferencesConverter()
    return HalHarvester(settings=get_app_settings(), converter=converter)


def test_hal_harvester_relevant_for_person_with_idhal(
        person_with_name_and_id_hal_i: Person,
        hal_harvester: HalHarvester,
):
    """Test that the harvester will run if submitted with an IDHAL."""
    assert hal_harvester.is_relevant(person_with_name_and_id_hal_i) is True


def test_hal_harvester_not_relevant_for_person_with_idref_only(
        person_with_name_and_idref: Person,
        hal_harvester: HalHarvester,
):
    """Test that the harvester will not run if submitted with only an IDREF."""
    assert hal_harvester.is_relevant(person_with_name_and_idref) is False


def test_hal_harvester_not_relevant_for_person_with_last_name_and_first_name_only(
        person_with_last_name_and_first_name: Person,
        hal_harvester: HalHarvester,
):
    """Test that the harvester will not run if submitted with only a last name."""
    assert hal_harvester.is_relevant(person_with_last_name_and_first_name) is False


@pytest.mark.asyncio
async def test_hal_harvester_finds_doc(hal_harvester: HalHarvester, hal_harvesting_db_model,
                                       reference_recorder_register_mock, hal_api_client_mock,
                                       async_session: AsyncSession):
    """Test that the harvester will find documents."""
    async_session.add(hal_harvesting_db_model)
    await async_session.commit()
    hal_harvester.set_harvesting_id(hal_harvesting_db_model.id)
    hal_harvester.set_entity_id(hal_harvesting_db_model.retrieval.entity_id)
    await hal_harvester.run()
    hal_api_client_mock.assert_called_once()
    reference_recorder_register_mock.assert_called_once()


@pytest.mark.asyncio
async def test_hal_harvester_registers_docs_in_db(hal_harvester: HalHarvester,
                                                  hal_harvesting_db_model,
                                                  hal_api_client_mock,
                                                  hal_api_docs_for_one_researcher: dict,
                                                  async_session: AsyncSession):
    """Test that after harvesting, the references are registered in the database."""
    async_session.add(hal_harvesting_db_model)
    await async_session.commit()
    hal_harvester.set_harvesting_id(hal_harvesting_db_model.id)
    hal_harvester.set_entity_id(hal_harvesting_db_model.retrieval.entity_id)
    await hal_harvester.run()
    hal_api_client_mock.assert_called_once()
    stmt = select(Reference, ReferenceEvent).join(ReferenceEvent).join(Harvesting).filter(
        Harvesting.id == hal_harvesting_db_model.id)
    result = (await async_session.execute(stmt)).unique()
    results = list(result)
    assert len(results) == 1
    reference = results[0][0]
    reference_event = results[0][1]
    assert reference.titles[0].value == \
           hal_api_docs_for_one_researcher.get('response').get('docs')[0].get('en_title_s')[0]
    assert reference.source_identifier == \
           hal_api_docs_for_one_researcher.get('response').get('docs')[0].get('docid')
    assert reference_event.type == ReferenceEvent.Type.CREATED.value
