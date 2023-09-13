"""Test the references API."""
from os import environ

from app.config import get_app_settings


def test_application_environment():
    """check that environment variables are properly read"""
    settings = get_app_settings()
    assert settings.app_env.name == "TEST"
    assert settings.api_prefix == "/api"


def test_yml_settings():
    settings = get_app_settings()
    assert settings.harvesters_settings_file.endswith("harvesters-tests.yml")
