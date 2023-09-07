"""
App settings base class
"""
import os

import yaml
from pydantic_settings import BaseSettings

from app.settings.app_env_types import AppEnvTypes


def lst_from_yml(yml_file: str) -> list[dict]:
    """
    Load settings from yml file
    """
    with open(yml_file) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


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

    harvesters_settings_file: str = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "..", "..", "harvesters.yml"
    )
    harvesters: list = lst_from_yml(harvesters_settings_file)
