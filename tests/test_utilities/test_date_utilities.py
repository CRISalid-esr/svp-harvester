import logging
from datetime import datetime, date

import pytest

from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.utilities.date_utilities import check_valid_iso8601_date


class TestCheckValidIso8601:
    """
    Test class for AbstractReferencesConverter
    """

    @pytest.mark.parametrize(
        "input_date, expected_output",
        [
            (None, None),  # Test with None
            ("2022-12-31", date(2022, 12, 31)),  # Test with date string
            (
                "2022-12-31T23:59:59",
                datetime(2022, 12, 31, 23, 59, 59),
            ),  # Test with datetime string
            (date(2022, 12, 31), date(2022, 12, 31)),  # Test with date object
            (
                datetime(2022, 12, 31, 23, 59, 59),
                datetime(2022, 12, 31, 23, 59, 59),
            ),  # Test with datetime object
        ],
    )
    def test_check_valid_iso8601_date(self, input_date, expected_output):
        """
        Test that _check_valid_iso8601_date returns the expected output with expected input
        """
        assert check_valid_iso8601_date(input_date) == expected_output

    @pytest.mark.parametrize(
        "invalid_date, expected_log",
        [
            (
                "invalid_date",
                "Could not parse date invalid_date from Unknown source with error",
            ),  # Test with invalid date string
            (
                123,
                "Invalid date 123 from Unknown source."
                " Date should be a string, datetime.date or datetime.datetime object",
            ),  # Test with non-string, non-date object
        ],
    )
    def test_check_valid_iso8601_date_with_invalid_date(
        self, invalid_date, expected_log, caplog
    ):
        """
        Test that _check_valid_iso8601_date logs the expected error message with invalid input
        """
        with caplog.at_level(logging.ERROR):
            assert check_valid_iso8601_date(invalid_date) is None
        assert expected_log in caplog.text
