"""Tests for the Person model."""
from app.harvesters.scanr.scanr_harvester import ScanrHarvester
from app.harvesters.scanr.scanr_references_converter import ScanrReferencesConverter
from app.models.people import Person


def test_scanr_harvester_relevant(person_with_name_and_idref: Person):
    """Test that the harvester will run if submitted with an IDREF."""
    harvester = ScanrHarvester(converter=ScanrReferencesConverter())
    assert harvester.is_relevant(person_with_name_and_idref) is False
