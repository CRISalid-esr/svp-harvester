from loguru import logger
from sqlalchemy import select
from app.db.abstract_dao import AbstractDAO
from app.db.models.issue import Issue


class IssueDAO(AbstractDAO):
    """
    Data access object for issues
    """

    async def get_issue_by_source_and_source_identifier(
        self,
        source: str,
        source_identifier: str,
    ) -> Issue | None:
        """
        Get an issue by its source and source identifier

        :param source: source of the issue
        :param source_identifier: source identifier of the issue
        :return: the issue or None if not found
        """
        query = (
            select(Issue)
            .where(Issue.source == source)
            .where(Issue.source_identifier == source_identifier)
        )
        logger.debug(f"Query get_issue_by_source_identifier_and_source: {query}")
        return await self.db_session.scalar(query)
