"""
Settings for test environment
"""
import logging

from pydantic_settings import SettingsConfigDict

from app.settings.app_settings import AppSettings


class TestAppSettings(AppSettings):
    """
    Settings for test environment
    """
    debug: bool = True

    logging_level: int = logging.DEBUG

    model_config = SettingsConfigDict(env_file='.test.env', extra='ignore')
