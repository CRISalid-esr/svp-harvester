"""
Identifiers model
"""
from enum import Enum

from pydantic import BaseModel


class IdentifierTypeEnum(str, Enum):
    """Identifier types"""

    IDREF = "idref"
    ID_HAL = "id_hal"
    ORCID = "orcid"


class Identifier(BaseModel):
    """Identifier model"""

    type: IdentifierTypeEnum
    value: str
