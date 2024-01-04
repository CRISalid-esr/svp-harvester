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
            contribution_role = Contribution.Role.UNKNOWN

        return contribution_role.value
