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

    amqp_user: str = "guest"
    amqp_password: str = "guest"
    amqp_host: str = "127.0.0.1"
    amqp_queue_name: str = "svp-harvester"
