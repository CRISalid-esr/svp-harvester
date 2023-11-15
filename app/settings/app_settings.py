"""
App settings base class
"""
import os

import yaml
from pydantic_settings import BaseSettings

from app.settings.app_env_types import AppEnvTypes


class AppSettings(BaseSettings):
    """
    App settings main class with parameters definition
    """

    @staticmethod
    def settings_file_path(filename: str) -> str:
        """
        Get the path of a settings file

        :param filename: The name of the settings file
        :return: The path of the settings file
        """
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", "..", filename
        )

    @staticmethod
    def lst_from_yml(yml_file: str) -> list[dict]:
        """
        Load settings from yml file
        """
        with open(yml_file, encoding="utf8") as file:
            return yaml.load(file, Loader=yaml.FullLoader)

    app_env: AppEnvTypes = AppEnvTypes.PROD
    debug: bool = False

    api_host: str = "http://localhost:8000"
    api_prefix: str = "/api"
    api_version: str = "v0"

    amqp_user: str = "guest"
    amqp_password: str = "guest"
    amqp_host: str = "127.0.0.1"
    amqp_queue_name: str = "svp-harvester"

    harvesters_settings_file: str = settings_file_path(filename="harvesters.yml")
    harvesters: list = lst_from_yml(yml_file=harvesters_settings_file)

    identifiers_settings_file: str = settings_file_path(filename="identifiers.yml")
    identifiers: list = lst_from_yml(yml_file=identifiers_settings_file)

    db_engine: str = "postgresql+asyncpg"
    db_name: str = "svp_harvester"
    db_user: str = "svp_harvester"
    db_password: str = "secret"
    db_host: str = "localhost"
    db_port: int = 5432

    scanr_es_host = "https://host_name.com/"
    scanr_es_publications_index = "publications-index-name"
    scanr_es_persons_index = "persons-index-name"
    scanr_es_user = "johndoe"
    scanr_es_pass = "pass"
