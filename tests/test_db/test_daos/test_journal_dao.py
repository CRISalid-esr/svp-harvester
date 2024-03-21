import pytest

from app.db.models.journal import Journal
from app.db.daos.journal_dao import JournalDAO


@pytest.mark.asyncio
async def test_get_journal_by_source_issn_or_eissn(async_session):
    """
    Test that we can get a journal by its source and issn or eissn.
    :param async_session: async session fixture
    :return: None
    """
    journal = Journal(
        source="hal",
        issn=["1234-5678"],
        eissn=["9876-5432"],
        issn_l="1234-5678",
        source_identifier="hal-1234-5678",
    )
    async_session.add(journal)
    await async_session.commit()

    dao = JournalDAO(async_session)
    journal_from_db = await dao.get_journal_by_source_issn_or_eissn_or_issn_l(
        "hal", issn=["1234-5678"]
    )
    assert isinstance(journal_from_db, Journal)
    assert "1234-5678" in journal_from_db.issn

    journal_from_db = await dao.get_journal_by_source_issn_or_eissn_or_issn_l(
        "hal", eissn=["9876-5432"]
    )
    assert isinstance(journal_from_db, Journal)
    assert "1234-5678" in journal_from_db.issn

    journal_from_db = await dao.get_journal_by_source_issn_or_eissn_or_issn_l(
        "hal", issn_l="1234-5678"
    )
    assert isinstance(journal_from_db, Journal)
    assert "1234-5678" in journal_from_db.issn


@pytest.mark.asyncio
async def test_get_without_issn_and_eissn(async_session):
    """
    Test that we can't get a journal by its source without issn or eissn.
    """

    journal = Journal(
        source="hal",
        source_identifier="hal-1234-5678",
        issn="1234-5678",
        eissn="9876-5432",
    )
    async_session.add(journal)
    await async_session.commit()

    dao = JournalDAO(async_session)
    journal_from_db = await dao.get_journal_by_source_issn_or_eissn_or_issn_l("hal")
    assert journal_from_db is None


@pytest.mark.asyncio
async def test_get_journal_by_source_identifier_and_source(async_session):
    """
    Test that we can get a journal by its source and source identifier.
    """

    journal = Journal(source="hal", source_identifier="hal-1234-5678")
    async_session.add(journal)
    await async_session.commit()

    dao = JournalDAO(async_session)
    journal_from_db = await dao.get_journal_by_source_identifier_and_source(
        "hal", "hal-1234-5678"
    )
    assert isinstance(journal_from_db, Journal)
    assert journal_from_db.source_identifier == "hal-1234-5678"
