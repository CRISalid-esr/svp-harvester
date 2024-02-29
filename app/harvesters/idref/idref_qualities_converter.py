from loguru import logger

from app.db.models.contribution import Contribution


class IdrefQualitiesConverter:
    """
    Use mapping table to convert idref role values to loc roles values
    """

    ROLES_MAPPING = {
        "aut": Contribution.Role.AUTHOR,
        "cur": Contribution.Role.UNKNOWN,
    }

    @staticmethod
    def convert(quality: str) -> str:
        """
        Convert science plus role value to loc role value
        :param quality: science plus role value
        :return: loc role value
        """
        if quality not in IdrefQualitiesConverter.ROLES_MAPPING:
            logger.warning(f"Unknown idref quality: {quality}")
            return Contribution.Role.UNKNOWN.value
        return IdrefQualitiesConverter.ROLES_MAPPING[quality].value
