from loguru import logger

from app.db.models.contribution import Contribution


class SciencePlusQualitiesConverter:
    """
    Use mapping table to convert science plus role values to loc roles values
    """

    ROLES_MAPPING = {
        "aut": Contribution.Role.AUTHOR,
        "ctb": Contribution.Role.CONTRIBUTOR,
        "cur": Contribution.Role.UNKNOWN,
    }

    @staticmethod
    def convert(quality: str) -> str:
        """
        Convert science plus role value to loc role value
        :param quality: science plus role value
        :return: loc role value
        """
        if quality not in SciencePlusQualitiesConverter.ROLES_MAPPING:
            logger.warning(f"Unknown science plus quality: {quality}")
            return Contribution.Role.UNKNOWN.value
        return SciencePlusQualitiesConverter.ROLES_MAPPING[quality].value
