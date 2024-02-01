import pytest

from app.harvesters.scanr.scanr_roles_converter import ScanrRolesConverter
from app.db.models.contribution import Contribution


def test_known_hal_qualities_converter():
    """
    Given a known quality from HAL
    When the quality converter is called
    Then the quality is converted into the corresponding Loc value
    """
    role = "enq"
    convert = ScanrRolesConverter.convert(role=role)

    assert convert == Contribution.Role.INTERVIEWER.value


def test_unknown_hal_qualities_converter():
    """
    Given an unknown quality
    When the quality converter is called
    Then the Unknown quality is returned
    """
    role = "test_method"
    convert = ScanrRolesConverter.convert(role=role)

    assert convert == Contribution.Role.UNKNOWN.value
