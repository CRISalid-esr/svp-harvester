from pydantic import BaseModel, ConfigDict, HttpUrl


class ReferenceManifestation(BaseModel):
    """
    Pydantic model matching Manifestation sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    page: HttpUrl
    download_url: HttpUrl | None = None
    additional_files: list[HttpUrl] | None = []
