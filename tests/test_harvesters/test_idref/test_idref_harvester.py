"""Tests for the Person model."""
from app.harvesters.idref.idref_harvester import IdrefHarvester
from app.harvesters.idref.idref_references_converter import IdrefReferencesConverter
from app.db.models.person import Person as DbPerson


def test_idref_harvester_relevant_with_idref(
    person_with_name_and_idref_db_model: DbPerson,
):
    """Test that the harvester will run if submitted with an IDREF."""
    harvester = IdrefHarvester(converter=IdrefReferencesConverter())
    assert harvester.is_relevant(person_with_name_and_idref_db_model) is True


def test_idref_harvester_relevant_with_orcid(
    person_with_name_and_orcid_db_model: DbPerson,
):
    """Test that the harvester will run if submitted with an ORCID."""
    harvester = IdrefHarvester(converter=IdrefReferencesConverter())
    assert harvester.is_relevant(person_with_name_and_orcid_db_model) is True
