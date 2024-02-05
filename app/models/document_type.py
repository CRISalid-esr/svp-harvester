from pydantic import BaseModel, ConfigDict


class DocumentType(BaseModel):
    """
    Pydantic model matching DocumentType sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    uri: str

    label: str | None
