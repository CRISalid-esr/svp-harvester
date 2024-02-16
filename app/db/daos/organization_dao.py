from sqlalchemy import select
from app.db.abstract_dao import AbstractDAO
from app.db.models.organization import Organization


class OrganizationDAO(AbstractDAO):
    """
    Data access object for organizations
    """

    async def get_organization_by_identifier(
        self, identifier: str
    ) -> Organization | None:
        """
        Get an organization by its identifier

        :param identifier: identifier of the organization
        :return: the organization or None if not found
        """
        query = select(Organization).where(Organization.source_identifier == identifier)
        return await self.db_session.scalar(query)
