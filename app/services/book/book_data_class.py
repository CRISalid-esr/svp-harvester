from attr import dataclass


@dataclass
class BookInformations:
    """
    Information about a book
    """

    source: str
    title: str = None
    isbn10: str = None
    isbn13: str = None
    publisher: str = None
