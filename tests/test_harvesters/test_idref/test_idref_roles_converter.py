from app.db.models.contribution import Contribution
from app.harvesters.idref.open_edition_roles_converter import (
    OpenEditionRolesConverter,
)


def test_known_open_edition_qualities_converter():
    """
    Given a known role from OpenEdition
    When the role converter is called
    Then the role is converted into the corresponding Loc value
    """
    role = "contributor"
    convert = OpenEditionRolesConverter.convert(role=role)
    expected_role = Contribution.get_url("CTB")
    assert convert == expected_role


def test_uknown_open_edition_qualities_converter(caplog):
    """
    Given an unknown role
    When the role converter is called
    Then the Unknown role is returned
    """
    role = "test_method"
    convert = OpenEditionRolesConverter.convert(role=role)
    expected_role = Contribution.get_url("UNKNOWN")
    assert convert == expected_role
    assert f"Unknown open edition role: {role}" in caplog.text
