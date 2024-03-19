"""
Settings for production environment
"""
import logging

from app.settings.app_settings import AppSettings


class ProdAppSettings(AppSettings):
    """
    Settings for production environment
    """

    debug: bool = False

    logging_level: int = logging.INFO

    loguru_level: str = "INFO"

    institution_name: str = "Please set the institution name in the settings file"
