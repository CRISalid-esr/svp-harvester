from pydantic import BaseModel, ConfigDict


class PublicationIdentifier(BaseModel):
    """
    Pydantic model matching PublicationIdentifier sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    type: str
    value: str
