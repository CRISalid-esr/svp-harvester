from pydantic import BaseModel, ConfigDict, Field


class LiteralField(BaseModel):
    """
    Pydantic model matching ReferenceLiteralField sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(exclude=True)

    value: str
    language: str | None
