from pydantic import BaseModel, ConfigDict, Field


class Label(BaseModel):
    """
    Pydantic model matching Label sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    value: str

    language: str | None

    preferred: bool = Field(exclude=True)
