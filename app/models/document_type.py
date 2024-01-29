from pydantic import BaseModel, ConfigDict, Field


class DocumentType(BaseModel):
    """
    Pydantic model matching DocumentType sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(exclude=True)

    uri: str

    label: str | None
