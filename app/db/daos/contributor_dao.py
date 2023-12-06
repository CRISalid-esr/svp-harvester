from sqlalchemy import select

from app.db.abstract_dao import AbstractDAO
from app.db.models.contributor import Contributor


class ContributorDAO(AbstractDAO):
    """
    Data access object for contributors
    """

    async def get_by_source_and_name(self, source: str, name: str) -> Contributor:
        """
        Get a contributor by source and name field
        :param source: source of the contributor ("hal", "idref"...)
        :param name: name of the contributor
        :return: contributor
        """
        stmt = (
            select(Contributor)
            .where(Contributor.source == source)
            .where(Contributor.name == name)
            # where source identifier is null
            .where(Contributor.source_identifier.is_(None))
        )
        return (await self.db_session.execute(stmt)).unique().scalars().one_or_none()

    async def get_by_source_and_identifier(
        self, source: str, source_identifier: str
    ) -> Contributor:
        """
        Get a contributor by source and source identifier
        :param source: source of the contributor ("hal", "idref"...)
        :param source_identifier: identifier of the contributor in the source
        :return: contributor
        """
        stmt = (
            select(Contributor)
            .where(Contributor.source == source)
            .where(Contributor.source_identifier == source_identifier)
        )
        return (await self.db_session.execute(stmt)).unique().scalars().one_or_none()
