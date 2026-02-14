"""
Person model
"""

from pydantic import ConfigDict, model_validator
from pydantic_core.core_schema import ValidationInfo

from app.config import get_app_settings
from app.models.entities import Entity


class Person(Entity):
    """
    Person identified by at least full name or one of the identifiers
    """

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def _check_minimal_information(cls, data: dict, _: ValidationInfo) -> dict:
        if identifier := data.get("identifiers"):
            # check that each identifier is a hash with type and value
            assert all(
                isinstance(i, dict) and i.get("type") and i.get("value")
                for i in identifier
            ), "Each identifier must be a hash with type and value"

        # check that there is at least one identifier
        valid_identifier_types = cls._valid_identifier_types()
        has_valid_identifier = any(
            identifier.get("type") in valid_identifier_types
            for identifier in data.get("identifiers", [])
        )

        # check if full_name is provided
        has_name = "name" in data and data["name"]

        # check that there is at least one identifier
        assert (
            has_valid_identifier or has_name
        ), "At least one identifier or the entire name must be provided"

        return data

    @model_validator(mode="before")
    @classmethod
    def _check_identifiers_referenced_in_settings(
        cls, data: dict, _: ValidationInfo
    ) -> dict:
        # check that all provider identifiers are referenced in settings
        # and list the invalid identifiers in assertion error message
        valid_identifier_types = cls._valid_identifier_types()
        invalid_identifiers = [
            identifier.get("type")
            for identifier in data.get("identifiers", [])
            if identifier.get("type") not in valid_identifier_types
        ]
        assert not invalid_identifiers, (
            f"Invalid identifiers: {', '.join(invalid_identifiers)}. "
            "Valid identifiers are:"
            f"{', '.join(valid_identifier_types)}"
        )
        return data

    def has_no_bibliographic_identifiers(self):
        """
        Check if the person has no bibliographic identifiers
        """
        valid_identifier_types = self._valid_identifier_types()
        return not any(
            identifier.type in valid_identifier_types for identifier in self.identifiers
        )

    @staticmethod
    def _valid_identifier_types() -> list[str]:
        valid_identifier_types = [
            identifier_type.get("key")
            for identifier_type in get_app_settings().identifiers
        ]
        return valid_identifier_types
