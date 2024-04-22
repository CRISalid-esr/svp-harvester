from loguru import logger

from app.db.models.contribution import Contribution


class PerseeQualitiesConverter:
    """
    Use mapping table to convert persee role value to loc roles values
    """

    ROLES_MAPPING = {
        "aut": Contribution.LOCAuthorRoles.AUT,
        "trl": Contribution.LOCAuthorRoles.TRL,
        "ctb": Contribution.LOCAuthorRoles.CTB,
    }

    @staticmethod
    def convert(quality: str) -> str:
        """
        Convert persee role value to loc role value
        :param quality: persee role value
        :return: loc role value
        """
        if quality not in PerseeQualitiesConverter.ROLES_MAPPING:
            logger.warning(f"Unknown persee quality: {quality}")
            return Contribution.LOCAuthorRoles.UNKNOWN.value
        return PerseeQualitiesConverter.ROLES_MAPPING[quality].value
