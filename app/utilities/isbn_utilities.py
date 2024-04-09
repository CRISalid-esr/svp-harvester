import isbnlib


def get_isbns(isbn: str | None) -> tuple[str | None, str | None]:
    """
    From an isbn check if it is a valid isbn10 or isbn13.
    If it is a valid isbn10, return it and convert to isbn13 also.
    If it is a valid isbn13, return it.

    :param isbn: str: isbn to check
    :return: tuple: (isbn10, isbn13)
    """
    isbn10 = None
    isbn13 = None
    if not isbn:
        return isbn10, isbn13

    if isbnlib.is_isbn10(isbn):
        isbn10 = isbn
        isbn13 = isbnlib.to_isbn13(isbn)
    elif isbnlib.is_isbn13(isbn):
        isbn13 = isbn

    isbn10 = _remove_carets(isbn10)
    isbn13 = _remove_carets(isbn13)

    return isbn10, isbn13


def _remove_carets(isbn: str | None) -> str | None:
    if not isbn:
        return isbn
    return isbn.replace("-", "")
