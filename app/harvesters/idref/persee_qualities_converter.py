from loguru import logger

from app.db.models.contribution import Contribution


class PerseeQualitiesConverter:
    """
    Use mapping table to convert persee role value to loc roles values
    """

    ROLES_MAPPING = {
        "aut": Contribution.Role.AUTHOR,
        "trl": Contribution.Role.TRANSLATOR,
        "ctb": Contribution.Role.CONTRIBUTOR,
    }

    @staticmethod
    def convert(quality: str) -> str:
        """
        Conver persee role value to loc role value
        :param quality: persee role value
        :return: loc role value
        """
        if quality not in PerseeQualitiesConverter.ROLES_MAPPING:
            logger.warning(f"Unknown persee quality: {quality}")
            return Contribution.Role.UNKNOWN.value
        return PerseeQualitiesConverter.ROLES_MAPPING[quality].value
