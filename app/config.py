"""
Settings loading module
"""
from functools import lru_cache
from typing import Dict, Type

from app.settings.app_env_types import AppEnvTypes
from app.settings.app_settings import AppSettings
from app.settings.development_settings import DevAppSettings
from app.settings.production_settings import ProdAppSettings
from app.settings.test_settings import TestAppSettings

environments: Dict[AppEnvTypes, Type[AppSettings]] = {
    AppEnvTypes.DEV: DevAppSettings,
    AppEnvTypes.PROD: ProdAppSettings,
    AppEnvTypes.TEST: TestAppSettings,
}


@lru_cache()
def get_app_settings() -> AppSettings:
    """
    Main entry point for settings loading

    :return: Settings fitting current environment
    """
    config = environments[AppSettings().app_env]
    return config()
