"""
Identifiers model
"""

from pydantic import BaseModel


class Identifier(BaseModel):
    """Identifier model"""

    type: str
    value: str
