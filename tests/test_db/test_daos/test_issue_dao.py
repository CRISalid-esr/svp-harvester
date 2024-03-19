import pytest

from app.db.daos.issue_dao import IssueDAO
from app.db.models.issue import Issue
from app.db.models.journal import Journal


@pytest.mark.asyncio
async def test_get_issue_by_source_and_source_identifier(async_session):
    """
    Test that we can get an issue by its source and source identifier.
    """
    journal = Journal(
        source="hal",
        source_identifier="hal-1234-5678",
        issn="1234-5678",
        eissn="9876-5432",
    )
    issue = Issue(
        source="hal",
        source_identifier="hal-1234-5678",
        journal=journal,
        journal_id=journal.id,
    )
    async_session.add(issue)
    await async_session.commit()

    dao = IssueDAO(async_session)
    issue_from_db = await dao.get_issue_by_source_and_source_identifier(
        "hal", "hal-1234-5678"
    )
    assert isinstance(issue_from_db, Issue)
    assert issue_from_db.source_identifier == "hal-1234-5678"
