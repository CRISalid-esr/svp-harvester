"""Tests for the Person model."""
from app.config import get_app_settings
from app.harvesters.idref.idref_harvester import IdrefHarvester
from app.models.people import Person


def test_idref_harvester_relevant(person_with_name_and_idref: Person):
    harvester = IdrefHarvester(get_app_settings())
    assert harvester.is_relevant(person_with_name_and_idref) is True
