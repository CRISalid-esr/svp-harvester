from loguru import logger

from app.db.models.contribution import Contribution


class IdrefQualitiesConverter:
    """
    Use mapping table to convert idref role values to loc roles values
    """

    @staticmethod
    def convert(quality: str) -> str:
        """
        Convert science plus role value to loc role value
        :param quality: science plus role value
        :return: loc role value
        """
        quality_upper = quality.upper()

        if hasattr(Contribution.LOCAuthorRoles, quality_upper):
            return getattr(Contribution.LOCAuthorRoles, quality_upper).loc_url()

        logger.warning(f"Unknown idref quality: {quality}")
        return Contribution.LOCAuthorRoles.UNKNOWN.loc_url()
