"""
Person model
"""
from typing import Optional

from pydantic import model_validator
from pydantic_core.core_schema import ValidationInfo

from app.models.entities import Entity
from app.models.identifiers import IdentifierTypeEnum


class Person(Entity):
    """
    Person identified by at least last name + first name or one of the identifiers
    """

    last_name: Optional[str] = None
    first_name: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _check_minimal_information(cls, data: dict, _: ValidationInfo) -> dict:
        # there is at least one identifier
        assert any(
            # pylint: disable=cell-var-from-loop
            list(filter(lambda h: h["type"] == t.value, data.get("identifiers") or []))
            for t in IdentifierTypeEnum
        ) or all(
            # or there are both first name and last name
            [data.get("last_name"), data.get("first_name")]
        ), "At least one identifier or the entire name must be provided"
        return data
