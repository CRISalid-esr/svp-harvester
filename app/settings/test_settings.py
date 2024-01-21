"""
Settings for test environment
"""
import logging
import os
import sys
from typing import ClassVar

from pydantic_settings import SettingsConfigDict
from pyparsing import TextIO

from app.settings.app_settings import AppSettings


class TestAppSettings(AppSettings):
    """
    Settings for test environment
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.harvesters_settings_file: str = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "..",
            "..",
            "tests",
            "harvesters-tests.yml",
        )
        try:
            self.harvesters = AppSettings.lst_from_yml(self.harvesters_settings_file)
        except FileNotFoundError:
            print(f">>FileNotFoundError: {self.harvesters_settings_file}")

        self.identifiers_settings_file: str = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "..",
            "..",
            "tests",
            "identifiers-tests.yml",
        )
        try:
            self.identifiers = AppSettings.lst_from_yml(self.identifiers_settings_file)
        except FileNotFoundError:
            print(f">>FileNotFoundError: {self.identifiers_settings_file}")

    debug: bool = True

    logging_level: int = logging.DEBUG

    loguru_level: str = "DEBUG"

    logger_sink: ClassVar[str | TextIO] = sys.stderr

    model_config = SettingsConfigDict(env_file=".test.env", extra="ignore")
