from attr import dataclass


@dataclass
class JournalInformations:
    """
    Information about a Journal
    """

    source: str
    source_identifier: str
    eissn: str = None
    issn: str = None
    publisher: str = None
    titles: list[str] = []
