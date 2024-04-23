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
    expected_quality = Contribution.get_url("EDT")

    assert convert == expected_quality


def test_unknown_hal_qualities_converter():
    """
    Given an unknown quality
    When the quality converter is called
    Then the Unknown quality is returned
    """
    quality = "test_method"
    convert = HalQualitiesConverter.convert(quality=quality)
    expected_quality = Contribution.get_url("UNKNOWN")

    assert convert == expected_quality
