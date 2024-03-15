from pydantic import BaseModel


class Journal(BaseModel):
    """
    Pydantic model matching Journal sql_alchemy model
    """

    source: str
    source_identifier: str

    issn: str | None = None
    eissn: str | None = None
    publisher: str | None = None

    titles: list[str] = []
