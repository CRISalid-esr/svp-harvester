import pytest

from app.services.identifiers.rules.hal_id_from_hal_url import HalIdFromHalUrlRule


@pytest.mark.parametrize(
    "url_to_test, expected_value",
    [
        ("https://shs.hal.science/halshs-02185511/file/Science%20paper%20ORI.pdf",
         "halshs-02185511"),
        ("https://shs.hal.science/halshs-02185511v4/file/Science%20paper%20ORI.pdf",
         "halshs-02185511"),
        ("https://shs.hal.science/jpa-02185511/file/Science%20paper%20ORI.pdf",
         "jpa-02185511"),
        ("https://shs.hal.science/invalid-02185511/file/Science%20paper%20ORI.pdf",
         None),
        ("https://shs.invalid.science/halshs-02185511/file/Science%20paper%20ORI.pdf",
         None)
    ],
    ids=[
        "test_extract_hal_id",
        "test_extract_hal_id_without_version",
        "test_extract_hal_id_with_alternate_known_pattern",
        "test_extract_hal_id_with_unknown_pattern",
        "test_extract_hal_id_with_invalid_netloc",
    ]
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
