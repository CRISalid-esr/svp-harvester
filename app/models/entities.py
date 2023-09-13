"""
Person model
"""
from typing import Optional, List

from pydantic import BaseModel

from app.models.identifiers import Identifier, IdentifierTypeEnum


class Entity(BaseModel):
    """
    Source entity (person, organization, etc.) for which references are retrieved
    """

    identifiers: List[Identifier] = []

    def get_identifier(self, identifier_type: IdentifierTypeEnum) -> Optional[str]:
        """

        :param identifier_type: Identifier type
        :return: identifier value or None if not defined
        """
        for identifier in self.identifiers:
            if identifier.type == identifier_type:
                return identifier.value
        return None
