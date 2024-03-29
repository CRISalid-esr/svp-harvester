from pydantic import BaseModel, ConfigDict


class Journal(BaseModel):
    """
    Pydantic model matching Journal sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    source: str
    source_identifier: str

    issn: list[str] = []
    eissn: list[str] = []
    issn_l: str | None = None
    publisher: str | None = None

    titles: list[str] = []
