"""Tests for the Person model."""
from app.harvesters.idref.idref_harvester import IdrefHarvester
from app.harvesters.idref.idref_references_converter import IdrefReferencesConverter
from app.models.people import Person


def test_idref_harvester_relevant(person_with_name_and_idref: Person):
    """Test that the harvester will run if submitted with an IDREF."""
    harvester = IdrefHarvester(converter=IdrefReferencesConverter())
    assert harvester.is_relevant(person_with_name_and_idref) is True
