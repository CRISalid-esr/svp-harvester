from pydantic import BaseModel, ConfigDict


class OrganizationIdentifier(BaseModel):
    """
    Pydantic model matching OrganizationIdentifier sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    type: str
    value: str
