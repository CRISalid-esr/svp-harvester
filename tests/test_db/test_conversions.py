"""Tests for the Person model."""

from app.db.conversions import EntityConverter
from app.models.people import Person


def test_person_without_identifiers_converter(person_without_identifiers: Person):
    """
    GIVEN a person without identifiers
    WHEN the person is converted to a DB model
    THEN check the DB model has the correct attributes

    :param person_without_identifiers: person without identifiers
    :return: None
    """
    converter = EntityConverter(person_without_identifiers)
    db_model = converter.to_db_model()
    assert db_model.__class__.__name__ == "Person"
    assert db_model.name == "John Doe"
    assert len(db_model.identifiers) == 0


def test_person_with_idref_converter(person_with_name_and_idref: Person):
    """
    GIVEN a person with name and IDREF
    WHEN the person is converted to a DB model
    THEN check the DB model has the correct attributes

    :param person_with_name_and_idref: person with name and IDREF
    :return:
    """
    converter = EntityConverter(person_with_name_and_idref)
    db_model = converter.to_db_model()
    assert db_model.__class__.__name__ == "Person"
    assert db_model.name == "John Doe"
    assert len(db_model.identifiers) == 1
    assert db_model.identifiers[0].type == "idref"
    assert db_model.identifiers[0].value == "123456789"
