import pytest

from app.db.models.identifier import Identifier as DbIdentifier
from app.db.models.person import Person as DbPerson


@pytest.fixture(name="person_with_name_and_idref_db_model")
def fixture_person_with_name_and_idref_db_model():
    """
    Generate a person with first name, last name and IDREF in DB model format
    :return: person with first name, last name and IDREF  in DB model format
    """
    return DbPerson(
        name="John Doe",
        identifiers=[DbIdentifier(type="idref", value="123456789")],
    )


@pytest.fixture(name="person_with_name_and_id_hal_i_db_model")
def fixture_person_with_name_and_id_hal_i_db_model():
    """
    Generate a person with first name, last name and Id_Hal_i in DB model format
    :return: person with first name, last name and Id_Hal_i  in DB model format
    """
    return DbPerson(
        name="John Doe",
        identifiers=[DbIdentifier(type="id_hal_i", value="123456789")],
    )


@pytest.fixture(name="person_with_name_and_id_hal_s_db_model")
def fixture_person_with_name_and_id_hal_s_db_model():
    """
    Generate a person with first name, last name and Id_Hal_s in DB model format
    :return: person with first name, last name and Id_Hal_s  in DB model format
    """
    return DbPerson(
        name="John Doe",
        identifiers=[DbIdentifier(type="id_hal_s", value="john-doe")],
    )


@pytest.fixture(name="person_with_name_and_id_hal_i_s_db_model")
def fixture_person_with_name_and_id_hal_i_s_db_model():
    """
    Generate a person with first name, last name and Id_Hal_i and Id_Hal_s in DB model format
    :return: person with first name, last name and Id_Hal_i and Id_Hal_s  in DB model format
    """
    return DbPerson(
        name="John Doe",
        identifiers=[
            DbIdentifier(type="id_hal_i", value="123456789"),
            DbIdentifier(type="id_hal_s", value="john-doe"),
        ],
    )
