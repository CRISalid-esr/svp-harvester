import pytest
from asyncpg import RaiseError
from sqlalchemy.exc import DBAPIError

from app.db.models.journal import Journal
from app.db.daos.journal_dao import JournalDAO


@pytest.mark.asyncio
async def test_creating_journal_with_used_issn_raises_exception(async_session):
    """
    Given a journal in database with issn "1234-5678" and "9876-5432"
    When we try to create a journal with issn "1234-5678"
    Then an exception should be raised

    :param async_session: async session fixture
    :return: None
    """
    journal1 = Journal(
        source="hal",
        issn=["1234-5678", "9876-5432"],
        eissn=["9876-5432"],
        issn_l="1234-5678",
        source_identifier="hal-1234-5678",
    )
    async_session.add(journal1)
    await async_session.commit()
    assert journal1.id is not None

    journal2 = Journal(
        source="hal",
        issn=["6789-1234", "1234-5678"],
        source_identifier="hal-6789-1234",
    )
    async_session.add(journal2)
    with pytest.raises(DBAPIError):
        await async_session.commit()
        assert journal2.id is None
