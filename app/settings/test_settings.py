"""
Settings for test environment
"""
import logging
import os

from pydantic_settings import SettingsConfigDict

from app.settings.app_settings import AppSettings, lst_from_yml


class TestAppSettings(AppSettings):
    """
    Settings for test environment
    """

    debug: bool = True

    logging_level: int = logging.DEBUG

    model_config = SettingsConfigDict(env_file=".test.env", extra="ignore")

    harvesters_settings_file: str = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        "..",
        "..",
        "tests",
        "harvesters-tests.yml",
    )

    harvesters: list[dict] = lst_from_yml(harvesters_settings_file)
