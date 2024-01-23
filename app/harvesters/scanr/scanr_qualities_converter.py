from app.db.models.contribution import Contribution


class ScanrQualitiesConverter:
    """
    Use mapping table to convert scanr role values to loc roles values
    """

    # TODO: Edit ROLES_MAPPING to replace the UNKNOWN values when the mapping is complete

    ROLES_MAPPING = {
        "ann": Contribution.Role.ANNOTATOR,
        "architecture": Contribution.Role.UNKNOWN,
        "ard": Contribution.Role.UNKNOWN,
        "author": Contribution.Role.AUTHOR,
        "coding": Contribution.Role.UNKNOWN,
        "co_first_author": Contribution.Role.AUTHOR,
        "co_last_author": Contribution.Role.AUTHOR,
        "com": Contribution.Role.UNKNOWN,
        "compiler": Contribution.Role.COMPILER,
        "csc": Contribution.Role.UNKNOWN,
        "ctb": Contribution.Role.CONTRIBUTOR,
        "ctg": Contribution.Role.UNKNOWN,
        "ctr": Contribution.Role.UNKNOWN,
        "cwt": Contribution.Role.UNKNOWN,
        "debugging": Contribution.Role.UNKNOWN,
        "design": Contribution.Role.UNKNOWN,
        "dev": Contribution.Role.UNKNOWN,
        "dir": Contribution.Role.UNKNOWN,
        "directeurthese": Contribution.Role.UNKNOWN,
        "dis": Contribution.Role.UNKNOWN,
        "documentation": Contribution.Role.UNKNOWN,
        "edt": Contribution.Role.EDITOR,
        "enq": Contribution.Role.INTERVIEWER,
        "ill": Contribution.Role.ILLUSTRATOR,
        "int": Contribution.Role.UNKNOWN,
        "interviewee": Contribution.Role.INTERVIEWEE,
        "maintenance": Contribution.Role.UNKNOWN,
        "management": Contribution.Role.UNKNOWN,
        "man": Contribution.Role.UNKNOWN,
        "med": Contribution.Role.UNKNOWN,
        "membrejury": Contribution.Role.UNKNOWN,
        "oth": Contribution.Role.OTHER,
        "pht": Contribution.Role.UNKNOWN,
        "presenter": Contribution.Role.UNKNOWN,
        "presidentjury": Contribution.Role.UNKNOWN,
        "preface_writer": Contribution.Role.AUTHOR_OF_INTRODUCTION,
        "pro": Contribution.Role.UNKNOWN,
        "prd": Contribution.Role.UNKNOWN,
        "project_manager": Contribution.Role.UNKNOWN,
        "rapporteur": Contribution.Role.UNKNOWN,
        "reporter": Contribution.Role.INTERVIEWER,
        "sad": Contribution.Role.UNKNOWN,
        "scientific_editor": Contribution.Role.SCIENTIFIC_EDITOR,
        "sds": Contribution.Role.UNKNOWN,
        "spk": Contribution.Role.UNKNOWN,
        "stm": Contribution.Role.UNKNOWN,
        "support": Contribution.Role.UNKNOWN,
        "testing": Contribution.Role.UNKNOWN,
        "trl": Contribution.Role.TRANSLATOR,
        "win": Contribution.Role.UNKNOWN,
        "wam": Contribution.Role.UNKNOWN,
    }

    @staticmethod
    def convert(quality: str) -> str:
        """
        Convert scanr role value to loc role value
        :param quality: scanr role value
        :return: loc role value
        """
        if quality in ScanrQualitiesConverter.ROLES_MAPPING:
            contribution_role = ScanrQualitiesConverter.ROLES_MAPPING[quality]
        else:
            contribution_role = Contribution.Role.UNKNOWN

        return contribution_role.value
