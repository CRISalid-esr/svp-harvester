from loguru import logger
from sqlalchemy import select
from app.db.abstract_dao import AbstractDAO
from app.db.models.journal import Journal


class JournalDAO(AbstractDAO):
    """
    Data access object for journals
    """

    async def get_journal_by_source_issn_or_eissn(
        self, source: str, issn: str = None, eissn: str = None
    ):
        """
        Get a journal by its source and issn or eissn

        :param source: source of the journal
        :param issn: issn of the journal
        :param eissn: eissn of the journal
        :return: the journal or None if not found
        """
        if issn is None and eissn is None:
            return None
        query = select(Journal).where(Journal.source == source)
        if issn is not None:
            query = query.where(Journal.issn == issn)
        if eissn is not None:
            query = query.where(Journal.eissn == eissn)
        logger.debug(f"Query get_journal_by_source_issn_or_eissn: {query}")
        return await self.db_session.scalar(query)

    async def get_journal_by_source_identifier_and_source(
        self, source: str, source_identifier: str
    ):
        """
        Get a journal by its source and source identifier

        :param source: source of the journal
        :param source_identifier: source identifier of the journal
        :return: the journal or None if not found
        """
        query = (
            select(Journal)
            .where(Journal.source == source)
            .where(Journal.source_identifier == source_identifier)
        )
        logger.debug(f"Query get_journal_by_source_identifier_and_source: {query}")
        return await self.db_session.scalar(query)
