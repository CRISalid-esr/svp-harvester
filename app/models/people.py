"""
Person model
"""
from typing import Optional

from pydantic import model_validator, ConfigDict
from pydantic_core.core_schema import ValidationInfo

from app.config import get_app_settings
from app.models.entities import Entity


class Person(Entity):
    """
    Person identified by at least last name + first name or one of the identifiers
    """

    model_config = ConfigDict(from_attributes=True)

    last_name: Optional[str] = None
    first_name: Optional[str] = None
    full_name: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _check_minimal_information(cls, data: dict, _: ValidationInfo) -> dict:
        settings = get_app_settings()
        if identifier := data.get("identifiers"):
            # check that each identifier is a hash with type and value
            assert all(
                isinstance(i, dict) and i.get("type") and i.get("value")
                for i in identifier
            ), "Each identifier must be a hash with type and value"

        # check that there is at least one identifier
        has_valid_identifier = any(
            # pylint: disable=cell-var-from-loop
            list(
                filter(
                    lambda h: h.get("type", None) == t.get("key"),
                    data.get("identifiers", []) or [],
                )
            )
            for t in settings.identifiers
        )

        # check if full_name is provided
        has_full_name = "full_name" in data and data["full_name"]

        # Check if both first name and last name are provided
        has_first_and_last_names = all(
            [data.get("last_name"), data.get("first_name")]
        )

        # check that there is at least one identifier
        assert has_valid_identifier or has_full_name or has_first_and_last_names,\
            "At least one identifier or the entire name must be provided"

        return data

    @model_validator(mode="before")
    @classmethod
    def _check_identifiers_referenced_in_settings(
        cls, data: dict, _: ValidationInfo
    ) -> dict:
        settings = get_app_settings()
        # check that all provider identifiers are referenced in settings
        # and list the invalid identifiers in assertion error message
        invalid_identifiers = [
            identifier.get("type")
            for identifier in data.get("identifiers", [])
            if identifier.get("type")
            not in [
                identifier_type.get("key") for identifier_type in settings.identifiers
            ]
        ]
        assert not invalid_identifiers, (
            f"Invalid identifiers: {', '.join(invalid_identifiers)}. "
            "Valid identifiers are:"
            f"{', '.join([identifier_type.get('key') for identifier_type in settings.identifiers])}"
        )
        return data
