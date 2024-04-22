from loguru import logger

from app.db.models.contribution import Contribution


class SciencePlusQualitiesConverter:
    """
    Use mapping table to convert science plus role values to loc roles values
    """

    ROLES_MAPPING = {
        "aut": Contribution.LOCAuthorRoles.AUT,
        "ctb": Contribution.LOCAuthorRoles.CTB,
    }

    @staticmethod
    def convert(quality: str) -> str:
        """
        Convert science plus role value to loc role value
        :param quality: science plus role value
        :return: loc role value
        """
        if quality not in SciencePlusQualitiesConverter.ROLES_MAPPING:
            logger.warning(f"Unknown science plus quality: {quality} {len(quality)}")
            return Contribution.LOCAuthorRoles.UNKNOWN.value
        return SciencePlusQualitiesConverter.ROLES_MAPPING[quality].value
