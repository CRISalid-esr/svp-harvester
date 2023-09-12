"""Tests for the Person model."""
from app.config import get_app_settings
from app.harvesters.scanr.scanr_harvester import ScanrHarvester
from app.models.people import Person


def test_scanr_harvester_relevant(person_with_name_and_idref: Person):
    harvester = ScanrHarvester(get_app_settings())
    assert harvester.is_relevant(person_with_name_and_idref) is True
