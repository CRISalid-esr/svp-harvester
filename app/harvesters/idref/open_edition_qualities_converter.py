from loguru import logger
from app.db.models.contribution import Contribution


class OpenEditionQualitiesConverter:
    """
    Use mapping table to convert open edition role values to loc roles values
    """

    ROLES_MAPPING = {
        "contributor": Contribution.Role.CONTRIBUTOR,
        "creator": Contribution.Role.AUTHOR,
    }

    @staticmethod
    def convert(quality: str) -> str:
        """
        Convert open edition role value to loc role value
        :param quality: open edition role value
        :return: loc role value
        """
        if quality not in OpenEditionQualitiesConverter.ROLES_MAPPING:
            logger.warning(f"Unknown open edition quality: {quality}")
            return Contribution.Role.UNKNOWN.value
        return OpenEditionQualitiesConverter.ROLES_MAPPING[quality].value
