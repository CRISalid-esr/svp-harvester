from loguru import logger
from app.db.models.contribution import Contribution


class OpenEditionRolesConverter:
    """
    Use mapping table to convert open edition role values to loc roles values
    """

    ROLES_MAPPING = {
        "contributor": Contribution.LOCAuthorRoles.CTB,
        "creator": Contribution.LOCAuthorRoles.AUT,
    }

    @staticmethod
    def convert(role: str) -> str:
        """
        Convert open edition role value to loc role value
        :param role: open edition role value
        :return: loc role value
        """
        if role not in OpenEditionRolesConverter.ROLES_MAPPING:
            logger.warning(f"Unknown open edition role: {role}")
            return Contribution.LOCAuthorRoles.UNKNOWN.loc_url()
        return OpenEditionRolesConverter.ROLES_MAPPING[role].loc_url()
