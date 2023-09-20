"""Tests for the Person model."""
import pytest

from app.config import get_app_settings
from app.harvesters.hal.hal_harvester import HalHarvester
from app.harvesters.hal.hal_references_converter import HalReferencesConverter
from app.models.people import Person


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
