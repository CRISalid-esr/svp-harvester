from typing import List
from sqlalchemy import select
from app.db.abstract_dao import AbstractDAO
from app.db.models.journal import Journal


class JournalDAO(AbstractDAO):
    """
    Data access object for journals
    """

    async def get_journal_by_source_issn_or_eissn_or_issn_l(
        self,
        source: str,
        issn: List[str] = None,
        eissn: List[str] = None,
        issn_l: str = None,
    ):
        """
        Get a journal by its source and issn or eissn

        :param source: source of the journal
        :param issn: issn of the journal
        :param eissn: eissn of the journal
        :return: the journal or None if not found
        """
        if not issn and not eissn and issn_l is None:
            return None
        if not issn:
            issn = []
        if not eissn:
            eissn = []
        query = select(Journal).where(Journal.source == source)
        for issn_value in issn:
            query = query.where(Journal.issn.any(issn_value))
        for eissn_value in eissn:
            query = query.where(Journal.eissn.any(eissn_value))
        if issn_l is not None:
            query = query.where(Journal.issn_l == str(issn_l))

        # Get the first result
        return (await self.db_session.execute(query)).scalars().first()

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
        return (await self.db_session.execute(query)).scalars().one_or_none()
