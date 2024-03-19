from attr import dataclass

from app.db.models.journal import Journal


@dataclass
class IssueInformations:
    """
    Information about an issue
    """

    source: str
    source_identifier: str
    journal: Journal
    number: list[str] = []
    volume: str | None = None
    date: str | None = None
    rights: str | None = None
    titles: list[str] = []
