"""Tests for the Person model."""
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.issue import Issue as DbIssue, Journal as DbJournal


@pytest.mark.asyncio
async def test_two_issues_cannot_have_same_source_and_identifier(
    async_session: AsyncSession,
):
    """
    GIVEN a Issue with a source and identifier
    WHEN another Issue with the same source and identifier is added
    THEN check a IntegrityError is raised
         due to violation of the unique constraint on source and identifier

    :param async_session: An async session fixture for the test database
    :return: None
    """

    journal1 = DbJournal(source="hal", source_identifier="1234", titles=["title"])

    issue_1 = DbIssue(
        source="hal", source_identifier="1234", titles=["title"], journal=journal1
    )

    async_session.add(issue_1)

    await async_session.commit()

    journal2 = DbJournal(source="hal", source_identifier="1234", titles=["Other title"])

    issue_2 = DbIssue(
        source="hal", source_identifier="1234", titles=["Other title"], journal=journal2
    )
    async_session.add(issue_2)

    with pytest.raises(IntegrityError):
        await async_session.commit()
