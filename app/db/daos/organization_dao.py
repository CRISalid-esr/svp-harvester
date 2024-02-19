from sqlalchemy import select, and_
from app.db.abstract_dao import AbstractDAO
from app.db.models.organization import Organization
from app.db.models.organization_identifier import OrganizationIdentifier


class OrganizationDAO(AbstractDAO):
    """
    Data access object for organizations
    """

    async def get_organization_by_source_identifier(
        self, identifier: str
    ) -> Organization | None:
        """
        Get an organization by its identifier

        :param identifier: identifier of the organization
        :return: the organization or None if not found
        """
        query = select(Organization).where(Organization.source_identifier == identifier)
        return await self.db_session.scalar(query)

    async def get_organization_by_identifiers(
        self, identifiers: list[OrganizationIdentifier]
    ) -> Organization | None:
        """
        Get an organization if any of its identifiers match the given list
        and cound is distinct
        """
        query = (
            select(Organization)
            .join(OrganizationIdentifier)
            .filter(
                and_(
                    OrganizationIdentifier.type.in_(
                        [identifier.type for identifier in identifiers]
                    ),
                    OrganizationIdentifier.value.in_(
                        [identifier.value for identifier in identifiers]
                    ),
                )
            )
        )
        return await self.db_session.scalar(query)
