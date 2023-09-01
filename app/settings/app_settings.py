"""
App settings base class
"""
from pydantic_settings import BaseSettings

from app.settings.app_env_types import AppEnvTypes


class AppSettings(BaseSettings):
    """
    App settings main class with parameters definition
    """

    app_env: AppEnvTypes = AppEnvTypes.PROD
    debug: bool = False

    api_prefix: str = "/api"
    api_version: str = "v0"
