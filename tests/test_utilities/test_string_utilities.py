from app.utilities.string_utilities import remove_after_separator


def test_with_separator():
    """
    GIVEN a string with multiples separators
    WHEN the string is sent to the remove_after_separator method
    THEN check that the method return the part of the string before the first separator
    """
    test_string = "Lorem ipsum / dolor sit / amet"
    expected_result = "Lorem ipsum"
    assert remove_after_separator(test_string, "/") == expected_result


def test_with_different_separator():
    """
    GIVEN a string with multiples separators
    WHEN the string is sent to the remove_after_separator method
    THEN check that the method return the part of the string
     before the first corresponding separator
    """
    test_string = "Lorem ipsum / dolor sit : amet"
    expected_result = "Lorem ipsum / dolor sit"
    assert remove_after_separator(test_string, ":") == expected_result


def test_without_separator():
    """
    GIVEN a string without any separator
    WHEN the string is sent to the remove_after_separator method
    THEN check that the method return the original string unchanged
    """
    test_string = "noseparator"
    expected_result = "noseparator"
    assert remove_after_separator(test_string, "/") == expected_result
