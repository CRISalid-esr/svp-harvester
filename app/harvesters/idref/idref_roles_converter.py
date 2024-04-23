from loguru import logger

from app.db.models.contribution import Contribution


class IdrefRolesConverter:
    """
    Use mapping table to convert idref role values to loc roles values
    """

    @staticmethod
    def convert(role: str) -> str:
        """
        Convert science plus role value to loc role value
        :param role: science plus role value
        :return: loc role value
        """
        role_upper = role.upper()

        if hasattr(Contribution.LOCAuthorRoles, role_upper):
            return getattr(Contribution.LOCAuthorRoles, role_upper).loc_url()

        logger.warning(f"Unknown idref role: {role}")
        return Contribution.LOCAuthorRoles.UNKNOWN.loc_url()
