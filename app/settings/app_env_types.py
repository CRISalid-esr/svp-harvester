from enum import Enum


class AppEnvTypes(Enum):
    """
    Enum for app environment types
    """
    PROD: str = "PROD"
    DEV: str = "DEV"
    TEST: str = "TEST"
