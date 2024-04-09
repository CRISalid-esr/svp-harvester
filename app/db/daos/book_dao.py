from sqlalchemy import or_, select
from app.db.abstract_dao import AbstractDAO
from app.db.models.book import Book


class BookDAO(AbstractDAO):
    """
    Data access object for books
    """

    async def get_books_by_isbn(
        self, source: str, isbn10: str | None = None, isbn13: str | None = None
    ) -> Book | None:
        """
        Get a book by its isbn10 and isbn13

        :param isbn10: isbn10 of the books
        :param isbn13: isbn13 of the books
        :return: the book or None if not found
        """
        if not isbn10 and not isbn13:
            return None
        query = select(Book).where(Book.source == source)
        isbn_filters = []
        if isbn10:
            isbn_filters.append(Book.isbn10 == isbn10)
        if isbn13:
            isbn_filters.append(Book.isbn13 == isbn13)
        if len(isbn_filters) > 0:
            query = query.where(or_(*isbn_filters))
        # Get the first result
        return (await self.db_session.execute(query)).scalars().first()

    async def get_books_by_title(
        self, source: str, title: str | None = None
    ) -> Book | None:
        """
        Get a book by its title

        :param title: title of the book
        :return: the book or None if not found
        """
        if not title:
            return None
        query = select(Book).where(Book.title == title).where(Book.source == source)
        return (await self.db_session.execute(query)).scalars().one_or_none()
