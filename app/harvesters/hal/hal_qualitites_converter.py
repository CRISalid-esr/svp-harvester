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
        "com": Contribution.Role.FILM_DIRECTOR,
        "rsp": Contribution.Role.RESPONDANT,
        "sds": Contribution.Role.SOUND_DESIGNER,
        "ctg": Contribution.Role.CARTOGRAPHER,
        "wam": Contribution.Role.WRITER_OF_ACCOMPANYING_MATERIAL,
        "ard": Contribution.Role.ARTISTIC_DIRECTOR,
        "prd": Contribution.Role.PRODUCTION_PERSONNEL,
        "management": Contribution.Role.SOFTWARE_DEVELOPER,
        "win": Contribution.Role.WITNESS,
        "design": Contribution.Role.SOFTWARE_DEVELOPER,
        "testing": Contribution.Role.SOFTWARE_DEVELOPER,
        "stm": Contribution.Role.STAGE_MANAGER,
        "maintenance": Contribution.Role.SOFTWARE_DEVELOPER,
        "support": Contribution.Role.SOFTWARE_DEVELOPER,
        "documentation": Contribution.Role.SOFTWARE_DEVELOPER,
        "ctr": Contribution.Role.CONTRIBUTOR,
        "dev": Contribution.Role.SOFTWARE_DEVELOPER,
        "debugging": Contribution.Role.SOFTWARE_DEVELOPER,
        "first": Contribution.Role.AUTHOR,
        "architecture": Contribution.Role.SOFTWARE_DEVELOPER,
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
