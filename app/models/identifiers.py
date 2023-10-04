"""
Identifiers model
"""

from pydantic import BaseModel, ConfigDict


class Identifier(BaseModel):
    """Identifier model"""

    model_config = ConfigDict(from_attributes=True)

    type: str
    value: str
