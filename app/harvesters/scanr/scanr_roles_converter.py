from app.db.models.contribution import Contribution


class ScanrRolesConverter:
    """
    Use mapping table to convert scanr role values to loc roles values
    """

    ROLES_MAPPING = {
        "ann": Contribution.LOCAuthorRoles.ANN,
        "architecture": Contribution.LOCAuthorRoles.SWD,
        "ard": Contribution.LOCAuthorRoles.ARD,
        "author": Contribution.LOCAuthorRoles.AUT,
        "coding": Contribution.LOCAuthorRoles.SWD,
        "co_first_author": Contribution.LOCAuthorRoles.AUT,
        "co_last_author": Contribution.LOCAuthorRoles.AUT,
        "com": Contribution.LOCAuthorRoles.FMD,
        "compiler": Contribution.LOCAuthorRoles.COM,
        "csc": Contribution.LOCAuthorRoles.SAD,
        "ctb": Contribution.LOCAuthorRoles.CTB,
        "ctg": Contribution.LOCAuthorRoles.CTG,
        "ctr": Contribution.LOCAuthorRoles.CTB,
        "cwt": Contribution.LOCAuthorRoles.CWT,
        "debugging": Contribution.LOCAuthorRoles.SWD,
        "design": Contribution.LOCAuthorRoles.SWD,
        "dev": Contribution.LOCAuthorRoles.SWD,
        "dir": Contribution.LOCAuthorRoles.FMD,
        "directeurthese": Contribution.LOCAuthorRoles.THS,
        "dis": Contribution.LOCAuthorRoles.DIS,
        "documentation": Contribution.LOCAuthorRoles.SWD,
        "edt": Contribution.LOCAuthorRoles.EDT,
        "enq": Contribution.LOCAuthorRoles.IVR,
        "ill": Contribution.LOCAuthorRoles.ILL,
        "int": Contribution.LOCAuthorRoles.SPK,
        "interviewee": Contribution.LOCAuthorRoles.IVE,
        "maintenance": Contribution.LOCAuthorRoles.SWD,
        "management": Contribution.LOCAuthorRoles.SWD,
        "man": Contribution.LOCAuthorRoles.ANL,
        "med": Contribution.LOCAuthorRoles.FLM,
        "membrejury": Contribution.LOCAuthorRoles.DGC,
        "oth": Contribution.LOCAuthorRoles.OTH,
        "pht": Contribution.LOCAuthorRoles.PHT,
        "presenter": Contribution.LOCAuthorRoles.SPK,
        "presidentjury": Contribution.LOCAuthorRoles.DGC,
        "preface_writer": Contribution.LOCAuthorRoles.AUI,
        "pro": Contribution.LOCAuthorRoles.FLM,
        "prd": Contribution.LOCAuthorRoles.PRD,
        "project_manager": Contribution.LOCAuthorRoles.PDR,
        "rapporteur": Contribution.LOCAuthorRoles.RAP,
        "reporter": Contribution.LOCAuthorRoles.IVR,
        "sad": Contribution.LOCAuthorRoles.SAD,
        "scientific_editor": Contribution.LOCAuthorRoles.EDC,
        "sds": Contribution.LOCAuthorRoles.SDS,
        "spk": Contribution.LOCAuthorRoles.SPK,
        "stm": Contribution.LOCAuthorRoles.STM,
        "support": Contribution.LOCAuthorRoles.SWD,
        "testing": Contribution.LOCAuthorRoles.SWD,
        "trl": Contribution.LOCAuthorRoles.TRL,
        "win": Contribution.LOCAuthorRoles.WIT,
        "wam": Contribution.LOCAuthorRoles.WAM,
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
            contribution_role = Contribution.LOCAuthorRoles.UNKNOWN

        return contribution_role.value
