from loguru import logger
from app.db.models.contribution import Contribution


class HalRolesConverter:
    """
    Use mapping table ton convert hal role values to loc roles values
    through a static method
    """

    ROLES_MAPPING = {
        "aut": Contribution.LOCAuthorRoles.AUT,
        "co_first_author": Contribution.LOCAuthorRoles.AUT,
        "co_last_author": Contribution.LOCAuthorRoles.AUT,
        "crp": Contribution.LOCAuthorRoles.AUT,
        "edt": Contribution.LOCAuthorRoles.EDT,
        "ctb": Contribution.LOCAuthorRoles.CTB,
        "ann": Contribution.LOCAuthorRoles.ANN,
        "trl": Contribution.LOCAuthorRoles.TRL,
        "compiler": Contribution.LOCAuthorRoles.COM,
        "scientific_editor": Contribution.LOCAuthorRoles.EDC,
        "ill": Contribution.LOCAuthorRoles.ILL,
        "interviewee": Contribution.LOCAuthorRoles.IVE,
        "reporter": Contribution.LOCAuthorRoles.IVR,
        "enq": Contribution.LOCAuthorRoles.IVR,
        "preface_writer": Contribution.LOCAuthorRoles.AUI,
        "presenter": Contribution.LOCAuthorRoles.SPK,
        "oth": Contribution.LOCAuthorRoles.OTH,
        "sad": Contribution.LOCAuthorRoles.SAD,
        "spk": Contribution.LOCAuthorRoles.SPK,
        "csc": Contribution.LOCAuthorRoles.SAD,
        "pro": Contribution.LOCAuthorRoles.FLM,
        "dir": Contribution.LOCAuthorRoles.FMD,
        "int": Contribution.LOCAuthorRoles.SPK,
        "coding": Contribution.LOCAuthorRoles.SWD,
        "man": Contribution.LOCAuthorRoles.ANL,
        "med": Contribution.LOCAuthorRoles.FLM,
        "pht": Contribution.LOCAuthorRoles.PHT,
        "project_manager": Contribution.LOCAuthorRoles.PDR,
        "cwt": Contribution.LOCAuthorRoles.CWT,
        "dis": Contribution.LOCAuthorRoles.DIS,
        "com": Contribution.LOCAuthorRoles.FMD,
        "rsp": Contribution.LOCAuthorRoles.RSP,
        "sds": Contribution.LOCAuthorRoles.SDS,
        "ctg": Contribution.LOCAuthorRoles.CTG,
        "wam": Contribution.LOCAuthorRoles.WAM,
        "ard": Contribution.LOCAuthorRoles.ARD,
        "prd": Contribution.LOCAuthorRoles.PRD,
        "management": Contribution.LOCAuthorRoles.SWD,
        "win": Contribution.LOCAuthorRoles.WIT,
        "design": Contribution.LOCAuthorRoles.SWD,
        "testing": Contribution.LOCAuthorRoles.SWD,
        "stm": Contribution.LOCAuthorRoles.STM,
        "maintenance": Contribution.LOCAuthorRoles.SWD,
        "support": Contribution.LOCAuthorRoles.SWD,
        "documentation": Contribution.LOCAuthorRoles.SWD,
        "ctr": Contribution.LOCAuthorRoles.CTB,
        "dev": Contribution.LOCAuthorRoles.SWD,
        "debugging": Contribution.LOCAuthorRoles.SWD,
        "first": Contribution.LOCAuthorRoles.AUT,
        "architecture": Contribution.LOCAuthorRoles.SWD,
    }

    @staticmethod
    def convert(role: str) -> str:
        """
        Convert hal role value to loc role value
        :param role: hal role value
        :return: loc role value
        """
        if role in HalRolesConverter.ROLES_MAPPING:
            contribution_role = HalRolesConverter.ROLES_MAPPING[role]
        else:
            logger.warning(f"Unknown hal role: {role}")
            contribution_role = Contribution.LOCAuthorRoles.UNKNOWN

        return contribution_role.loc_url()
