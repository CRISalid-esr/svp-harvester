from pydantic import BaseModel, ConfigDict


class ReferenceLiteralField(BaseModel):
    """
    Pydantic model matching ReferenceLiteralField sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    value: str
    language: str | None
