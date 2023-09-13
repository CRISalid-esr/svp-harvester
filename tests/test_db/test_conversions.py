"""Tests for the Person model."""

from app.db.conversions import EntityConverter
from app.models.identifiers import IdentifierTypeEnum
from app.models.people import Person


def test_person_without_identifiers_converter(person_without_identifiers: Person):
    converter = EntityConverter(person_without_identifiers)
    db_model = converter.to_db_model()
    assert db_model.__class__.__name__ == "Person"
    assert db_model.last_name == "Doe"
    assert db_model.first_name == "John"
    assert len(db_model.identifiers) == 0


def test_person_with_idref_converter(person_with_name_and_idref: Person):
    converter = EntityConverter(person_with_name_and_idref)
    db_model = converter.to_db_model()
    assert db_model.__class__.__name__ == "Person"
    assert db_model.last_name == "Doe"
    assert db_model.first_name == "John"
    assert len(db_model.identifiers) == 1
    assert db_model.identifiers[0].type == IdentifierTypeEnum.IDREF
    assert db_model.identifiers[0].value == "123456789"
