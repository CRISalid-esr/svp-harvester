from loguru import logger

from app.db.models.contribution import Contribution


class SudocQualitiesConverter:
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
    def convert(quality: str) -> str:
        """
        Convert sudo role value to loc role value
        :param quality: sudoc role value
        :return: loc role value
        """
        if quality not in SudocQualitiesConverter.ROLES_MAPPING:
            logger.warning(f"Unknown sudoc quality: {quality}")
            return Contribution.LOCAuthorRoles.UNKNOWN.value
        return SudocQualitiesConverter.ROLES_MAPPING[quality].value
