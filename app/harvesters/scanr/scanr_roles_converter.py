from app.db.models.contribution import Contribution


class ScanrRolesConverter:
    """
    Use mapping table to convert scanr role values to loc roles values
    """

    ROLES_MAPPING = {
        "ann": Contribution.Role.ANNOTATOR,
        "architecture": Contribution.Role.ARCHITECT,
        "ard": Contribution.Role.ARTISTIC_DIRECTOR,
        "author": Contribution.Role.AUTHOR,
        "coding": Contribution.Role.SOFTWARE_DEVELOPER,
        "co_first_author": Contribution.Role.AUTHOR,
        "co_last_author": Contribution.Role.AUTHOR,
        "com": Contribution.Role.FILM_DIRECTOR,
        "compiler": Contribution.Role.COMPILER,
        "csc": Contribution.Role.SCIENTIFIC_ADVISOR,
        "ctb": Contribution.Role.CONTRIBUTOR,
        "ctg": Contribution.Role.CARTOGRAPHER,
        "ctr": Contribution.Role.CONTRACTOR,
        "cwt": Contribution.Role.COMMENTATOR_OF_WRITTEN_TEXT,
        "debugging": Contribution.Role.SOFTWARE_DEVELOPER,
        "design": Contribution.Role.DESIGNER,
        "dev": Contribution.Role.SOFTWARE_DEVELOPER,
        "dir": Contribution.Role.FILM_DIRECTOR,
        "directeurthese": Contribution.Role.THESIS_ADVISOR,
        "dis": Contribution.Role.DISSERTANT,
        "documentation": Contribution.Role.UNKNOWN,
        "edt": Contribution.Role.EDITOR,
        "enq": Contribution.Role.INTERVIEWER,
        "ill": Contribution.Role.ILLUSTRATOR,
        "int": Contribution.Role.SPEAKER,
        "interviewee": Contribution.Role.INTERVIEWEE,
        "maintenance": Contribution.Role.UNKNOWN,
        "management": Contribution.Role.UNKNOWN,
        "man": Contribution.Role.ANALYST,
        "med": Contribution.Role.FILM_EDITOR,
        "membrejury": Contribution.Role.DEGREE_COMMITTEE_MEMBER,
        "oth": Contribution.Role.OTHER,
        "pht": Contribution.Role.PHOTOGRAPHER,
        "presenter": Contribution.Role.SPEAKER,
        "presidentjury": Contribution.Role.UNKNOWN,
        "preface_writer": Contribution.Role.AUTHOR_OF_INTRODUCTION,
        "pro": Contribution.Role.FILM_EDITOR,
        "prd": Contribution.Role.PRODUCTION_PERSONNEL,
        "project_manager": Contribution.Role.PROJECT_DIRECTOR,
        "rapporteur": Contribution.Role.UNKNOWN,
        "reporter": Contribution.Role.INTERVIEWER,
        "sad": Contribution.Role.SCIENTIFIC_ADVISOR,
        "scientific_editor": Contribution.Role.SCIENTIFIC_EDITOR,
        "sds": Contribution.Role.SOUND_DESIGNER,
        "spk": Contribution.Role.SPEAKER,
        "stm": Contribution.Role.STAGE_MANAGER,
        "support": Contribution.Role.UNKNOWN,
        "testing": Contribution.Role.UNKNOWN,
        "trl": Contribution.Role.TRANSLATOR,
        "win": Contribution.Role.WRITER_OF_INTRODUCTION,
        "wam": Contribution.Role.WRITER_OF_ACCOMPANYING_MATERIAL,
    }

    @staticmethod
    def convert(role: str) -> str:
        """
        Convert scanr role value to loc role value
        :param role: scanr role value
        :return: loc role value
        """
        if role in ScanrRolesConverter.ROLES_MAPPING:
            contribution_role = ScanrRolesConverter.ROLES_MAPPING[role]
        else:
            contribution_role = Contribution.Role.UNKNOWN

        return contribution_role.value
