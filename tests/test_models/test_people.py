"""Tests for the Person model."""
import pytest
from pydantic import ValidationError

from app.models.identifiers import IdentifierTypeEnum
from app.models.people import Person


def test_person_without_identifiers(person_without_identifiers: Person):
    """
    GIVEN a person without identifiers
    WHEN the person is created
    THEN check the person has the correct attributes
    :param person_without_identifiers: person without identifiers
    """
    assert person_without_identifiers.first_name == "John"
    assert person_without_identifiers.last_name == "Doe"
    assert person_without_identifiers.get_identifier("idref") is None


def test_person_with_name_and_idref(person_with_name_and_idref: Person):
    """
    GIVEN a person with name and IDREF
    WHEN the person is created
    THEN check the person has the correct attributes
    :param person_with_name_and_idref: person with name and IDREF
    """
    assert person_with_name_and_idref.first_name == "John"
    assert person_with_name_and_idref.last_name == "Doe"
    assert person_with_name_and_idref.get_identifier(IdentifierTypeEnum.IDREF) == "123456789"


def test_person_with_last_name_only():
    """
    GIVEN a person with only last name
    WHEN the person is created
    THEN check a validation error is raised
    """
    with pytest.raises(
        ValidationError,
        match="At least one identifier or the entire name must be provided",
    ):
        Person(last_name="Doe")
