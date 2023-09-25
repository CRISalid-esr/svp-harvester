from pydantic import BaseModel, ConfigDict


class LiteralFields(BaseModel):
    """
    Pydantic model matching LiteralFields sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    id: int

    value: str
    language: str
