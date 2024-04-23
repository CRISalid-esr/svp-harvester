from loguru import logger

from app.db.models.contribution import Contribution

# TODO: Complete the IdrefQualitiesConverter class to use LOCAuthorRoles enum by default,
#  without needing mapping table


class IdrefQualitiesConverter:
    """
    Use mapping table to convert idref role values to loc roles values
    """

    ROLES_MAPPING = {
        "aut": Contribution.LOCAuthorRoles.AUT,
        "cur": Contribution.LOCAuthorRoles.CUR,
        "ths": Contribution.LOCAuthorRoles.THS,
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
            return Contribution.LOCAuthorRoles.UNKNOWN.loc_url()
        return IdrefQualitiesConverter.ROLES_MAPPING[quality].loc_url()
