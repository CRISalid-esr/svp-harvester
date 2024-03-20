from typing import List
from attr import dataclass


@dataclass
class JournalInformations:
    """
    Information about a Journal
    """

    source: str
    source_identifier: str
    eissn: List[str] = []
    issn: List[str] = []
    issn_l: str = None
    publisher: str = None
    titles: list[str] = []
