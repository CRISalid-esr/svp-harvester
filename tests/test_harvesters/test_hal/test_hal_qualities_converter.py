import pytest

from app.harvesters.hal.hal_qualitites_converter import HalQualitiesConverter
from app.db.models.contribution import Contribution


def test_known_hal_qualities_converter():
    """
    Given a known quality from HAL
    When the quality converter is called
    Then the quality is converted into the corresponding Loc value
    """
    quality = "edt"
    convert = HalQualitiesConverter.convert(quality=quality)

    assert convert == Contribution.LOCAuthorRoles.EDT.value


def test_unknown_hal_qualities_converter():
    """
    Given an unknown quality
    When the quality converter is called
    Then the Unknown quality is returned
    """
    quality = "test_method"
    convert = HalQualitiesConverter.convert(quality=quality)

    assert convert == Contribution.LOCAuthorRoles.UNKNOWN.value
