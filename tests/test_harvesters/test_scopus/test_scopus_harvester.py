from unittest import mock
from sqlalchemy.ext.asyncio import AsyncSession

import aiohttp
import pytest

from app.db.models.person import Person
from app.harvesters.scopus.scopus_harvester import ScopusHarvester
from app.harvesters.scopus.scopus_references_converter import ScopusReferencesConverter


@pytest.fixture(name="scopus_client_mock")
def fixture_scopus_client_mock(scopus_xml_doc):
    """Retrieval service mock to detect run method calls"""

    with mock.patch.object(aiohttp.ClientSession, "get") as aiohttp_client_session_get:
        aiohttp_client_session_get.return_value.__aenter__.return_value.status = 200
        aiohttp_client_session_get.return_value.__aenter__.return_value.text.return_value = (
            scopus_xml_doc
        )
        yield aiohttp_client_session_get


@pytest.fixture(name="scopus_harvester")
def fixture_scopus_harvester() -> ScopusHarvester:
    """Fixture for a ScopusHarvester instance"""
    converter = ScopusReferencesConverter()
    return ScopusHarvester(converter=converter)


def test_scopus_relevant_for_person_with_scopus_eid(
    person_with_name_and_scopus_eid_db_model, scopus_harvester
):
    """Test that the harvester will run if submitted with an EID"""
    assert (
        scopus_harvester.is_relevant(person_with_name_and_scopus_eid_db_model) is True
    )


def test_scopus_not_relevant_for_person(
    person_with_name_and_id_hal_i, scopus_harvester
):
    """Test that the harvester will not run if sumbitted without an EID"""
    assert scopus_harvester.is_relevant(person_with_name_and_id_hal_i) is False


@pytest.mark.integration
@pytest.mark.asyncio
async def test_scopus_harvester_find_doc(
    scopus_harvester: ScopusHarvester,
    scopus_client_mock,
    reference_recorder_register_mock,
    scopus_harvesting_db_model_scopus_eid,
    async_session: AsyncSession,
):
    """Test that the harvester will find documents"""
    async_session.add(scopus_harvesting_db_model_scopus_eid)
    await async_session.commit()
    scopus_harvester.set_harvesting_id(scopus_harvesting_db_model_scopus_eid.id)
    scopus_harvester.set_entity_id(
        scopus_harvesting_db_model_scopus_eid.retrieval.entity_id
    )
    await scopus_harvester.run()
    scopus_client_mock.assert_called_once()
    reference_recorder_register_mock.assert_called_once()
