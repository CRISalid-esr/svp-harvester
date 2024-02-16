from pydantic import BaseModel, ConfigDict


class Organization(BaseModel):
    """
    Pydantic model matching Organization sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    source: str
    source_identifier: str
    name: str
