from unittest import mock
import aiohttp
import pytest

from app.db.models.contributor_identifier import ContributorIdentifier
from app.db.models.person import Person
from app.harvesters.open_alex.open_alex_harvester import OpenAlexHarvester
from app.harvesters.open_alex.open_alex_references_converter import (
    OpenAlexReferencesConverter,
)


@pytest.fixture(name="open_alex_client_mock")
def fixture_open_alex_client_mock():
    """Retrieval service mock to detect run method calls"""
    with mock.patch.object(aiohttp.ClientSession, "get") as aiohttp_client_session_get:
        aiohttp_client_session_get.return_value.__aenter__.return_value.status = 200
        aiohttp_client_session_get.return_value.__aenter__.return_value.json.return_value = ()
        yield aiohttp_client_session_get


@pytest.fixture(name="open_alex_harvester")
def fixture_open_alex_harvester() -> OpenAlexHarvester:
    """Fixture for a OpenAlexHarvester isntance"""
    converter = OpenAlexReferencesConverter(name="openalex")
    return OpenAlexHarvester(converter)


@pytest.mark.asyncio
async def test_open_alex_relevant_for_person_with_orcid(
    person_with_name_and_orcid_db_model: Person, open_alex_harvester
):
    """Test that the harvester is relevant after set_entity_id selects an orcid identifier."""
    with mock.patch.object(
        OpenAlexHarvester, "_get_entity", new=mock.AsyncMock(
            return_value=person_with_name_and_orcid_db_model
        )
    ):
        await open_alex_harvester.set_entity_id(1)
    assert open_alex_harvester.is_relevant() is True
    assert open_alex_harvester.entity_identifier_used[0] == (
        ContributorIdentifier.IdentifierType.ORCID.value
    )


@pytest.mark.asyncio
async def test_open_alex_not_relevant_for_person(
    person_with_name_and_id_hal_i_db_model: Person, open_alex_harvester
):
    """Test that the harvester is not relevant when entity has no orcid identifier."""
    with mock.patch.object(
        OpenAlexHarvester, "_get_entity", new=mock.AsyncMock(
            return_value=person_with_name_and_id_hal_i_db_model
        )
    ):
        await open_alex_harvester.set_entity_id(1)
    assert open_alex_harvester.is_relevant() is False
    assert open_alex_harvester.entity_identifier_used is None
