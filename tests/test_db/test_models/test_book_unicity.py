"""Tests for the Book model unicity constraint."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.book import Book


@pytest.mark.asyncio
async def test_two_books_cant_have_the_same_source_and_isbn(
    async_session: AsyncSession,
):
    """
    GIVEN a database with a Book model
    WHEN two books with the same source and isbn10 or isbn13 are added
    THEN an IntegrityError is raised for the duplicate entries

    :param async_session: An async session fixture for the test database
    :return: None
    """
    book1 = Book(
        source="hal",
        title="Book 1",
        isbn10="1234567890",
        isbn13="1234567890123",
        publisher="Publisher 1",
    )
    async_session.add(book1)
    await async_session.commit()

    book2 = Book(
        source="hal",
        title="Book 2",
        isbn10="1234567890",
        isbn13="1234567890124",
        publisher="Publisher 2",
    )
    async_session.add(book2)
    with pytest.raises(IntegrityError):
        await async_session.commit()
    await async_session.rollback()

    book3 = Book(
        source="hal",
        title="Book 3",
        isbn10="1234567891",
        isbn13="1234567890123",
        publisher="Publisher 3",
    )
    async_session.add(book3)
    with pytest.raises(IntegrityError):
        await async_session.commit()
    await async_session.rollback()


@pytest.mark.asyncio
async def test_books_can_have_same_isbn_with_different_sources(
    async_session: AsyncSession,
):
    """
    GIVEN a database with a Book model
    WHEN two books with the same isbn10 or isbn13 but different sources are added
    THEN no IntegrityError is raised

    :param async_session: An async session fixture for the test database
    :return: None
    """
    book1 = Book(
        source="hal",
        title="Book 1",
        isbn10="1234567890",
        isbn13="1234567890123",
        publisher="Publisher 1",
    )
    async_session.add(book1)
    await async_session.commit()

    # Create a second book with the same isbn10 but different source
    book2 = Book(
        source="scopus",
        title="Book 2",
        isbn10="1234567890",
        isbn13="1234567890124",
        publisher="Publisher 2",
    )
    async_session.add(book2)
    await async_session.commit()

    # Create a third book with the same isbn13 but different source
    book3 = Book(
        source="source3",
        title="Book 3",
        isbn10="1234567891",
        isbn13="1234567890123",
        publisher="Publisher 3",
    )
    async_session.add(book3)
    await async_session.commit()
