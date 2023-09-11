"""
Settings for development environment
"""
import logging

from pydantic_settings import SettingsConfigDict

from app.settings.app_settings import AppSettings


class DevAppSettings(AppSettings):
    """
    Settings for development environment
    """

    debug: bool = True

    logging_level: int = logging.DEBUG
    loguru_level: str = "DEBUG"

    model_config = SettingsConfigDict(env_file=".dev.env", extra="ignore")
