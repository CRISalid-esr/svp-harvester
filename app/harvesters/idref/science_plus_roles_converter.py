from loguru import logger

from app.db.models.contribution import Contribution


class SciencePlusRolesConverter:
    """
    Use mapping table to convert science plus role values to loc roles values
    """

    ROLES_MAPPING = {
        "aut": Contribution.LOCAuthorRoles.AUT,
        "ctb": Contribution.LOCAuthorRoles.CTB,
    }

    @staticmethod
    def convert(role: str) -> str:
        """
        Convert science plus role value to loc role value
        :param role: science plus role value
        :return: loc role value
        """
        if role not in SciencePlusRolesConverter.ROLES_MAPPING:
            logger.warning(f"Unknown science plus role: {role} {len(role)}")
            return Contribution.LOCAuthorRoles.UNKNOWN.loc_url()
        return SciencePlusRolesConverter.ROLES_MAPPING[role].loc_url()
