from typing import List
from pydantic import BaseModel, ConfigDict

from app.models.organization_identifier import OrganizationIdentifier


class Organization(BaseModel):
    """
    Pydantic model matching Organization sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    source: str
    source_identifier: str
    name: str
    type: str | None = None
    identifiers: List[OrganizationIdentifier] = []
