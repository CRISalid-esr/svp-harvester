from enum import Enum

from pydantic import BaseModel, ConfigDict

from app.models.references import Reference


class ReferenceEvent(BaseModel):
    """
    Pydantic model matching ReferenceEvent sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    id: int

    type: str

    reference: Reference

    enhanced: bool

    class Type(str, Enum):
        """Reference events types"""

        CREATED = "created"
        UPDATED = "updated"
        DELETED = "deleted"
        UNCHANGED = "unchanged"
