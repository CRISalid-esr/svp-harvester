"""
Person model
"""
from typing import Optional, List

from pydantic import BaseModel, ConfigDict

from app.models.identifiers import Identifier


class Entity(BaseModel):
    """
    Source entity (person, organization, etc.) for which references are retrieved
    """

    model_config = ConfigDict(from_attributes=True) | {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Foo",
                    "identifiers": [
                        {"type": "idref", "value": "123456789"},
                        {"type": "orcid", "value": "0000-0002-1825-0097"},
                    ],
                }
            ]
        }
    }

    identifiers: List[Identifier] = []

    name: Optional[str] = None

    def get_identifier(self, identifier_type: str) -> Optional[str]:
        """

        :param identifier_type: Identifier type
        :return: identifier value or None if not defined
        """
        for identifier in self.identifiers:
            if identifier.type == identifier_type:
                return identifier.value
        return None
