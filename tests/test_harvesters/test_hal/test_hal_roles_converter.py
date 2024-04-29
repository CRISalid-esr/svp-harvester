from app.harvesters.hal.hal_roles_converter import HalRolesConverter
from app.db.models.contribution import Contribution


def test_known_hal_qualities_converter():
    """
    Given a known role from HAL
    When the role converter is called
    Then the role is converted into the corresponding Loc value
    """
    role = "edt"
    convert = HalRolesConverter.convert(role=role)
    expected_role = Contribution.get_url("EDT")

    assert convert == expected_role


def test_unknown_hal_qualities_converter():
    """
    Given an unknown role
    When the role converter is called
    Then the Unknown role is returned
    """
    role = "test_method"
    convert = HalRolesConverter.convert(role=role)
    expected_role = Contribution.get_url("UNKNOWN")

    assert convert == expected_role
