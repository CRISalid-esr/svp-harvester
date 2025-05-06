import pytest

from app.services.identifiers.rules.hal_id_from_hal_url import HalIdFromHalUrlRule

import pytest


@pytest.mark.current
@pytest.mark.parametrize(
    "url_to_test, expected_value",
    [
        (
            "https://shs.hal.science/halshs-02185511/file/Science%20paper%20ORI.pdf",
            "halshs-02185511",
        ),
        (
            "https://shs.hal.science/halshs-02185511v4/file/Science%20paper%20ORI.pdf",
            "halshs-02185511",
        ),
        (
            "https://shs.hal.science/jpa-02185511/file/Science%20paper%20ORI.pdf",
            "jpa-02185511",
        ),
        (
            "https://shs.hal.science/invalid-02185511/file/Science%20paper%20ORI.pdf",
            None,
        ),
        (
            "https://shs.invalid.science/halshs-02185511/file/Science%20paper%20ORI.pdf",
            None,
        ),
        ("shs.hal.science/jpa-02185511/file/Science%20paper%20ORI.pdf", None),
        (None, None),
        ("https://halshs.archives-ouvertes.fr/halshs-02008468", "halshs-02008468"),
        ("https://hal.archives-ouvertes.fr/halshs-02008468", "halshs-02008468"),
    ],
    ids=[
        "test_extract_hal_id",
        "test_extract_hal_id_without_version",
        "test_extract_hal_id_with_alternate_known_pattern",
        "test_extract_hal_id_with_unknown_pattern",
        "test_extract_hal_id_with_invalid_netloc",
        "test_extract_hal_id_with_unknown_url_scheme",
        "test_extract_hal_id_without_url",
        "test_extract_hal_id_from_halshs_archives_ouvertes",
        "test_extract_hal_id_from_hal_archives_ouvertes",
    ],
)
def test_hal_id_from_hal_url(url_to_test, expected_value):
    """
    Test the extract_hal_id function in HalIdFromHalUrlRule Class
    :param url_to_test:
    :param expected_value:
    :return:
    """
    class_to_test = HalIdFromHalUrlRule()
    returned_value = class_to_test.extract_hal_id(url_to_test)
    assert returned_value == expected_value


def test_extract_hal_id_check_loguru_warning(caplog):
    """
    Test the extract_hal_id function logs a warning for unknown HAL patterns
    """
    url_to_test = (
        "https://shs.hal.science/invalid-02185511/file/Science%20paper%20ORI.pdf"
    )
    class_to_test = HalIdFromHalUrlRule()
    returned_value = class_to_test.extract_hal_id(url_to_test)
    expected_warning = "Unknown HAL identifier pattern: invalid-02185511"
    expected_value = None
    assert returned_value == expected_value
    assert expected_warning in caplog.text
