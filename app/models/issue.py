from pydantic import BaseModel, ConfigDict

from app.db.models.journal import Journal


class Issue(BaseModel):
    """
    Pydantic model matching Issue sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    source: str
    source_identifier: str

    titles: list[str] = []
    volume: str | None = None
    number: list[str] = []

    rights: str | None = None
    date: str | None = None

    journal: Journal
