from pydantic import BaseModel, ConfigDict, Field


class Contributor(BaseModel):
    """
    Pydantic model matching Contributor sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(exclude=True)

    source: str

    source_identifier: str | None

    name: str

    name_variants: list[str] = []
