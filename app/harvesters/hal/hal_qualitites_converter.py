from loguru import logger
from app.db.models.contribution import Contribution


class HalQualitiesConverter:
    """
    Use mapping table ton convert hal role values to loc roles values
    through a static method
    """

    ROLES_MAPPING = {
        "aut": Contribution.Role.AUTHOR,
        "co_first_author": Contribution.Role.AUTHOR,
        "co_last_author": Contribution.Role.AUTHOR,
        "crp": Contribution.Role.CORRESPONDENT_AUTHOR,
        "edt": Contribution.Role.EDITOR,
        "ctb": Contribution.Role.CONTRIBUTOR,
        "ann": Contribution.Role.ANNOTATOR,
        "trl": Contribution.Role.TRANSLATOR,
        "compiler": Contribution.Role.COMPILER,
        "scientific_editor": Contribution.Role.SCIENTIFIC_EDITOR,
        "ill": Contribution.Role.ILLUSTRATOR,
        "interviewee": Contribution.Role.INTERVIEWEE,
        "reporter": Contribution.Role.INTERVIEWER,
        "enq": Contribution.Role.INTERVIEWER,
        "preface_writer": Contribution.Role.AUTHOR_OF_INTRODUCTION,
        "presenter": Contribution.Role.SPEAKER,
        "oth": Contribution.Role.OTHER,
        "sad": Contribution.Role.SCIENTIFIC_ADVISOR,
        "spk": Contribution.Role.SPEAKER,
        "csc": Contribution.Role.SCIENTIFIC_ADVISOR,
        "pro": Contribution.Role.FILM_EDITOR,
        "dir": Contribution.Role.FILM_DIRECTOR,
        "int": Contribution.Role.SPEAKER,
        "coding": Contribution.Role.SOFTWARE_DEVELOPER,
        "man": Contribution.Role.ANALYST,
        "med": Contribution.Role.FILM_EDITOR,
        "pht": Contribution.Role.PHOTOGRAPHER,
        "project_manager": Contribution.Role.PROJECT_DIRECTOR,
        "cwt": Contribution.Role.COMMENTATOR_OF_WRITTEN_TEXT,
        "dis": Contribution.Role.DISSERTANT,
        "com": Contribution.Role.UNKNOWN,
        "rsp": Contribution.Role.UNKNOWN,
        "sds": Contribution.Role.UNKNOWN,
        "ctg": Contribution.Role.UNKNOWN,
        "wam": Contribution.Role.UNKNOWN,
        "ard": Contribution.Role.UNKNOWN,
        "prd": Contribution.Role.UNKNOWN,
        "management": Contribution.Role.UNKNOWN,
        "win": Contribution.Role.UNKNOWN,
        "design": Contribution.Role.UNKNOWN,
        "testing": Contribution.Role.UNKNOWN,
        "stm": Contribution.Role.UNKNOWN,
        "maintenance": Contribution.Role.UNKNOWN,
        "support": Contribution.Role.UNKNOWN,
        "documentation": Contribution.Role.UNKNOWN,
        "ctr": Contribution.Role.UNKNOWN,
        "dev": Contribution.Role.UNKNOWN,
        "debugging": Contribution.Role.UNKNOWN,
        "first": Contribution.Role.UNKNOWN,
    }

    @staticmethod
    def convert(quality: str) -> str:
        """
        Convert hal role value to loc role value
        :param quality: hal role value
        :return: loc role value
        """
        if quality in HalQualitiesConverter.ROLES_MAPPING:
            contribution_role = HalQualitiesConverter.ROLES_MAPPING[quality]
        else:
            logger.warning(f"Unknown hal quality: {quality}")
            contribution_role = Contribution.Role.UNKNOWN

        return contribution_role.value
