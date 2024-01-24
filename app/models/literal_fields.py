from pydantic import BaseModel, ConfigDict


class LiteralField(BaseModel):
    """
    Pydantic model matching ReferenceLiteralField sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    id: int

    value: str
    language: str | None
