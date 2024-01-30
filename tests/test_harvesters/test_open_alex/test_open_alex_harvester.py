from unittest import mock
import aiohttp
import pytest

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
    converter = OpenAlexReferencesConverter()
    return OpenAlexHarvester(converter)


def test_open_alex_relevant_for_person_with_orcid(
    person_with_name_and_orcid: Person, open_alex_harvester
):
    """Test that the harvester will run if submitted with an ORCID"""
    assert open_alex_harvester.is_relevant(person_with_name_and_orcid) is True


def test_open_alex_not_relevant_for_person(
    person_with_name_and_id_hal_i: Person, open_alex_harvester
):
    """Test that the harvester will not run if sumbitted without an ORCID"""
    assert open_alex_harvester.is_relevant(person_with_name_and_id_hal_i) is False
