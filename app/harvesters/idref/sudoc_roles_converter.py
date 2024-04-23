from loguru import logger

from app.db.models.contribution import Contribution


class SudocRolesConverter:
    """
    Use mapping table to convert sudoc role values to loc roles values
    """

    ROLES_MAPPING = {
        "aut": Contribution.LOCAuthorRoles.AUT,
        "trl": Contribution.LOCAuthorRoles.TRL,
        "opn": Contribution.LOCAuthorRoles.OPN,
        "ths": Contribution.LOCAuthorRoles.THS,
        "pra": Contribution.LOCAuthorRoles.PRA,
        "edt": Contribution.LOCAuthorRoles.EDT,
        "pbd": Contribution.LOCAuthorRoles.PBD,
        "aui": Contribution.LOCAuthorRoles.AUI,
        "clb": Contribution.LOCAuthorRoles.CTB,
        "fmo": Contribution.LOCAuthorRoles.FMO,
        "dnr": Contribution.LOCAuthorRoles.DNR,
        "cur": Contribution.LOCAuthorRoles.CUR,
        "aft": Contribution.LOCAuthorRoles.AFT,
        "ive": Contribution.LOCAuthorRoles.IVE,
        "ctg": Contribution.LOCAuthorRoles.CTG,
        "ill": Contribution.LOCAuthorRoles.ILL,
    }

    @staticmethod
    def convert(role: str) -> str:
        """
        Convert sudo role value to loc role value
        :param role: sudoc role value
        :return: loc role value
        """
        if role not in SudocRolesConverter.ROLES_MAPPING:
            logger.warning(f"Unknown sudoc role: {role}")
            return Contribution.LOCAuthorRoles.UNKNOWN.loc_url()
        return SudocRolesConverter.ROLES_MAPPING[role].loc_url()
