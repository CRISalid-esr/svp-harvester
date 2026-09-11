import pytest

from app.utilities.orcid_utilities import normalize_orcid


@pytest.mark.parametrize(
    "input_value, expected",
    [
        ("0000000218250097", "0000-0002-1825-0097"),
        ("0000000215568374", "0000-0002-1556-8374"),
        ("0000-0002-1825-0097", "0000-0002-1825-0097"),
        ("0000-0002-1556-8374", "0000-0002-1556-8374"),
    ],
)
def test_normalize_orcid(input_value, expected):
    assert normalize_orcid(input_value) == expected
