from loguru import logger

from app.db.models.contribution import Contribution


class SudocQualitiesConverter:
    """
    Use mapping table to convert sudoc role values to loc roles values
    """

    ROLES_MAPPING = {
        "aut": Contribution.Role.UNKNOWN,
        "trl": Contribution.Role.UNKNOWN,
        "opn": Contribution.Role.UNKNOWN,
        "ths": Contribution.Role.UNKNOWN,
        "pra": Contribution.Role.UNKNOWN,
        "edt": Contribution.Role.UNKNOWN,
        "pbd": Contribution.Role.UNKNOWN,
        "aui": Contribution.Role.UNKNOWN,
        "clb": Contribution.Role.UNKNOWN,
        "fmo": Contribution.Role.UNKNOWN,
        "dnr": Contribution.Role.UNKNOWN,
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
            return Contribution.Role.UNKNOWN.value
        return SudocQualitiesConverter.ROLES_MAPPING[quality].value
