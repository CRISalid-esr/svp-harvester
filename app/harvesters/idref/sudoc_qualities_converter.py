from loguru import logger

from app.db.models.contribution import Contribution


class SudocQualitiesConverter:
    """
    Use mapping table to convert sudoc role values to loc roles values
    """

    ROLES_MAPPING = {
        "aut": Contribution.Role.AUTHOR,
        "trl": Contribution.Role.TRANSLATOR,
        "opn": Contribution.Role.OPPONENT,
        "ths": Contribution.Role.THESIS_ADVISOR,
        "pra": Contribution.Role.PRAESES,
        "edt": Contribution.Role.EDITOR,
        "pbd": Contribution.Role.PUBLISHOR_DIRECTOR,
        "aui": Contribution.Role.AUTHOR_OF_INTRODUCTION,
        "clb": Contribution.Role.CONTRIBUTOR,
        "fmo": Contribution.Role.FORMER_OWNER,
        "dnr": Contribution.Role.DONOR,
        "cur": Contribution.Role.CURATOR,
        "aft": Contribution.Role.AUTHOR_OF_AFTERWORD,
        "ive": Contribution.Role.INTERVIEWEE,
        "ctg": Contribution.Role.CARTOGRAPHER,
        "ill": Contribution.Role.ILLUSTRATOR,
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
