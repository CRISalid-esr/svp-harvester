from loguru import logger

from app.db.models.contribution import Contribution


class PerseeRolesConverter:
    """
    Use mapping table to convert persee role value to loc roles values
    """

    ROLES_MAPPING = {
        "aut": Contribution.LOCAuthorRoles.AUT,
        "trl": Contribution.LOCAuthorRoles.TRL,
        "ctb": Contribution.LOCAuthorRoles.CTB,
    }

    @staticmethod
    def convert(role: str) -> str:
        """
        Convert persee role value to loc role value
        :param role: persee role value
        :return: loc role value
        """
        if role not in PerseeRolesConverter.ROLES_MAPPING:
            logger.warning(f"Unknown persee role: {role}")
            return Contribution.LOCAuthorRoles.UNKNOWN.loc_url()
        return PerseeRolesConverter.ROLES_MAPPING[role].loc_url()
