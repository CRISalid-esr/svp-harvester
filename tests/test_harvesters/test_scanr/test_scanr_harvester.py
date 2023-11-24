"""Tests for the Person model."""
from app.harvesters.scanr.scanr_harvester import ScanrHarvester
from app.harvesters.scanr.scanr_references_converter import ScanrReferencesConverter
from app.models.people import Person


# TODO: Do a test the same way test is made in test_references_history_safe_mode
def test_scanr_harvester_relevant_with_idref(person_with_name_and_idref: Person):
    """Test that the harvester will run if submitted with an IDREF."""
    harvester = ScanrHarvester(converter=ScanrReferencesConverter())
    assert harvester.is_relevant(person_with_name_and_idref) is True


def test_scanr_harvester_relevant_without_idref(person_with_name_and_orcid: Person):
    """Test that the harvester will run if submitted with an IDREF."""
    harvester = ScanrHarvester(converter=ScanrReferencesConverter())
    assert harvester.is_relevant(person_with_name_and_orcid) is False
