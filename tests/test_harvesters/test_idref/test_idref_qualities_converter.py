from app.db.models.contribution import Contribution
from app.harvesters.idref.open_edition_qualities_converter import (
    OpenEditionQualitiesConverter,
)


def test_known_open_edition_qualities_converter():
    # TODO WHEN Mapping Table is complete
    """
    Given a known quality from OpenEdition
    When the quality converter is called
    Then the quality is converted into the corresponding Loc value
    """
    quality = "author"
    convert = OpenEditionQualitiesConverter.convert(quality=quality)


def test_uknown_open_edition_qualities_converter(caplog):
    """
    Given an unknown quality
    When the quality converter is called
    Then the Unknown quality is returned
    """
    quality = "test_method"
    convert = OpenEditionQualitiesConverter.convert(quality=quality)
    assert convert == Contribution.Role.UNKNOWN.value
    assert f"Unknown open edition quality: {quality}" in caplog.text
