from enum import Enum
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.affiliations import affiliations_table
from app.db.session import Base
from app.db.models.organization import Organization  # pylint: disable=unused-import

RELATORS_BASE_URL = "https://id.loc.gov/vocabulary/relators/"


class Contribution(Base):
    """
    Model for persistence of contributions
    """

    class Role(Enum):
        """
        Rôles of contributors
        see https://documentation.abes.fr/aidescienceplusabes/index.html#roles
        """

        ANNOTATOR = "Annotator"
        ANALYST = "Analyst"
        ARCHITECT = "Architect"
        ARTISTIC_DIRECTOR = "Artistic Director"
        AUTHOR = "Author"
        AUTHOR_OF_AFTERWORD = "Author Of Afterword"
        AUTHOR_OF_INTRODUCTION = "Author Of Introduction"
        CARTOGRAPHER = "Cartographer"
        COMMENTATOR_OF_WRITTEN_TEXT = "Commentator Of Written Text"
        COMPOSER = "Composer"
        COMPILER = "Compiler"
        CONTRIBUTOR = "Contributor"
        CONTRACTOR = "Contractor"
        CORRESPONDENT_AUTHOR = "Correspondent Author"
        CURATOR = "Curator"
        DEGREE_COMMITTEE_MEMBER = "Degree Committee Member"
        DESIGNER = "Designer"
        DISSERTANT = "Dissertant"
        DONOR = "Donor"
        EDITOR = "Editor"
        FILM_DIRECTOR = "Film Director"
        FILM_EDITOR = "Film Editor"
        FORMER_OWNER = "Former Owner"
        ILLUSTRATOR = "Illustrator"
        INTERVIEWEE = "Interviewee"
        INTERVIEWER = "Interviewer"
        OPPONENT = "Opponent"
        OTHER = "Other"
        PHOTOGRAPHER = "Photographer"
        PRAESES = "Praeses"
        PRODUCER = "Producer"
        PROJECT_DIRECTOR = "Project Director"
        PRODUCTION_PERSONNEL = "Production Personnel"
        PUBLISHER_DIRECTOR = "Publisher Director"
        RESPONDANT = "Respondant"
        RAPPORTEUR = "Rapporteur"
        SCIENTIFIC_ADVISOR = "Scientific Advisor"
        SCIENTIFIC_EDITOR = "Scientific Editor"
        SOFTWARE_DEVELOPER = "Software Developer"
        SOUND_DESIGNER = "Sound Designer"
        SPEAKER = "Speaker"
        STAGE_MANAGER = "Stage Manager"
        THESIS_ADVISOR = "Thesis Advisor"
        TRANSLATOR = "Translator"
        UNKNOWN = "Unknown"
        WITNESS = "Witness"
        WRITER_OF_ACCOMPANYING_MATERIAL = "Writer Of Accompanying Material"
        WRITER_OF_INTRODUCTION = "Writer Of Introduction"

    # TODO: Move the existing harvesters from using the Role enum to the LOCAuthorRoles enum.
    #  This will require updating the existing harvesters to use the new enum.
    #  In case of the information sent back by the idref base harvester,
    #  the codes are already those of the LOCAuthorRoles enum.
    #  If the code is not set in the harvester, the role will be set to "Unknown".
    class LOCAuthorRoles(Enum):

        act = ("Actor", f"{RELATORS_BASE_URL}act.html")
        adp = ("Adapter", f"{RELATORS_BASE_URL}adp.html")
        anm = ("Animator", f"{RELATORS_BASE_URL}anm.html")
        ant = ("Bibliographic antecedent", f"{RELATORS_BASE_URL}ant.html")
        ann = ("Annotator", f"{RELATORS_BASE_URL}ann.html")
        anl = ("Analyst", f"{RELATORS_BASE_URL}anl.html")
        arr = ("Arranger", f"{RELATORS_BASE_URL}arr.html")
        art = ("Artist", f"{RELATORS_BASE_URL}art.html")
        ard = ("Artistic Director", f"{RELATORS_BASE_URL}ard.html")
        asg = ("Assignee", f"{RELATORS_BASE_URL}asg.html")
        asn = ("Associated name", f"{RELATORS_BASE_URL}asn.html")
        auc = ("Auctioneer", f"{RELATORS_BASE_URL}auc.html")
        aut = ("Author", f"{RELATORS_BASE_URL}aut.html")
        aqt = ("Author in quotations or text abstracts", f"{RELATORS_BASE_URL}aqt.html")
        aft = ("Author of afterword, colophon, etc.", f"{RELATORS_BASE_URL}aft.html")
        aui = ("Author of introduction, etc.", f"{RELATORS_BASE_URL}aui.html")
        aus = ("Screenwriter", f"{RELATORS_BASE_URL}aus.html")
        bnd = ("Binder", f"{RELATORS_BASE_URL}bnd.html")
        bdd = ("Binding designer", f"{RELATORS_BASE_URL}bdd.html")
        bkd = ("Book designer", f"{RELATORS_BASE_URL}bkd.html")
        bpd = ("Bookplate producer", f"{RELATORS_BASE_URL}bpd.html")
        bjd = ("Bookjacket designer", f"{RELATORS_BASE_URL}bjd.html")
        bsl = ("Bookseller", f"{RELATORS_BASE_URL}bsl.html")
        cll = ("Calligrapher", f"{RELATORS_BASE_URL}cll.html")
        ctg = ("Cartographer", f"{RELATORS_BASE_URL}ctg.html")
        cns = ("Censor", f"{RELATORS_BASE_URL}cns.html")
        chr = ("Choreographer", f"{RELATORS_BASE_URL}chr.html")
        clb = ("Collaborator", f"discontinued code")
        col = ("Collector", f"{RELATORS_BASE_URL}col.html")
        cmm = ("Commentator", f"{RELATORS_BASE_URL}cmm.html")
        cmt = ("Compositor", f"{RELATORS_BASE_URL}cmt.html")
        cwt = ("Commentator for written text", f"{RELATORS_BASE_URL}cwt.html")
        com = ("Compiler", f"{RELATORS_BASE_URL}com.html")
        cmp = ("Composer", f"{RELATORS_BASE_URL}cmp.html")
        ccp = ("Conceptor", f"{RELATORS_BASE_URL}ccp.html")
        cnd = ("Conductor", f"{RELATORS_BASE_URL}cnd.html")
        csp = ("Consultant to a project", f"{RELATORS_BASE_URL}csp.html")
        ctb = ("Contributor", f"{RELATORS_BASE_URL}ctb.html")
        cph = ("Copyright holder", f"{RELATORS_BASE_URL}cph.html")
        crr = ("Corrector", f"{RELATORS_BASE_URL}crr.html")
        cur = ("Curator", f"{RELATORS_BASE_URL}cur.html")
        dnc = ("Dancer", f"{RELATORS_BASE_URL}dnc.html")
        dte = ("Dedicatee", f"{RELATORS_BASE_URL}dte.html")
        dto = ("Dedicator", f"{RELATORS_BASE_URL}dto.html")
        dgc = ("Degree committee member", f"{RELATORS_BASE_URL}dgc.html")
        dgg = ("Degree granting institution", f"{RELATORS_BASE_URL}dgg.html")
        dis = ("Dissertant", f"{RELATORS_BASE_URL}dis.html")
        drt = ("Director", f"{RELATORS_BASE_URL}drt.html")
        dst = ("Distributor", f"{RELATORS_BASE_URL}dst.html")
        dnr = ("Donor", f"{RELATORS_BASE_URL}dnr.html")
        dub = ("Dubious author", f"{RELATORS_BASE_URL}dub.html")
        edc = ("Editor of compilation", f"{RELATORS_BASE_URL}edc.html")
        edt = ("Editor", f"{RELATORS_BASE_URL}edt.html")
        egr = ("Engraver", f"{RELATORS_BASE_URL}egr.html")
        etr = ("Etcher", f"{RELATORS_BASE_URL}etr.html")
        exp = ("Expert", f"{RELATORS_BASE_URL}exp.html")
        fmd = ("Film director", f"{RELATORS_BASE_URL}fmd.html")
        flm = ("Film editor", f"{RELATORS_BASE_URL}flm.html")
        frg = ("Forger", f"{RELATORS_BASE_URL}frg.html")
        fmo = ("Former owner", f"{RELATORS_BASE_URL}fmo.html")
        grt = ("Graphic technician", f"Discontinued code")
        hnr = ("Honoree", f"{RELATORS_BASE_URL}hnr.html")
        ilu = ("Illuminator", f"{RELATORS_BASE_URL}ilu.html")
        ill = ("Illustrator", f"{RELATORS_BASE_URL}ill.html")
        ins = ("Inscriber", f"{RELATORS_BASE_URL}ins.html")
        ive = ("Interviewee", f"{RELATORS_BASE_URL}ive.html")
        ivr = ("Interviewer", f"{RELATORS_BASE_URL}ivr.html")
        inv = ("Inventor", f"{RELATORS_BASE_URL}inv.html")
        isb = ("Issuing body", f"{RELATORS_BASE_URL}isb.html")
        lbt = ("Librettist", f"{RELATORS_BASE_URL}lbt.html")
        lse = ("Licensee", f"{RELATORS_BASE_URL}lse.html")
        lso = ("Licensor", f"{RELATORS_BASE_URL}lso.html")
        ltg = ("Lithographer", f"{RELATORS_BASE_URL}ltg.html")
        lyr = ("Lyricist", f"{RELATORS_BASE_URL}lyr.html")
        mte = ("Metal-engraver", f"{RELATORS_BASE_URL}mte.html")
        mon = ("Monitor", f"{RELATORS_BASE_URL}mon.html")
        mus = ("Musician", f"{RELATORS_BASE_URL}mus.html")
        nrt = ("Narrator", f"{RELATORS_BASE_URL}nrt.html")
        osp = ("Onscreen presenter", f"{RELATORS_BASE_URL}osp.html")
        opn = ("Opponent", f"{RELATORS_BASE_URL}opn.html")
        orm = ("Organizer", f"{RELATORS_BASE_URL}orm.html")
        org = ("Originator", f"{RELATORS_BASE_URL}org.html")
        oth = ("Other", f"{RELATORS_BASE_URL}oth.html")
        ppm = ("Papermaker", f"{RELATORS_BASE_URL}ppm.html")
        pop = ("Printer of plate", f"{RELATORS_BASE_URL}pop.html")
        pth = ("Patent holder", f"{RELATORS_BASE_URL}pth.html")
        prf = ("Performer", f"{RELATORS_BASE_URL}prf.html")
        pht = ("Photographer", f"{RELATORS_BASE_URL}pht.html")
        pra = ("Praeses", f"{RELATORS_BASE_URL}pra.html")
        prt = ("Printer", f"{RELATORS_BASE_URL}prt.html")
        pro = ("Producer", f"{RELATORS_BASE_URL}pro.html")
        prd = ("Production personnel", f"{RELATORS_BASE_URL}prd.html")
        prg = ("Programmer", f"{RELATORS_BASE_URL}prg.html")
        pdr = ("Project director", f"{RELATORS_BASE_URL}pdr.html")
        pfr = ("Proofreader", f"{RELATORS_BASE_URL}pfr.html")
        pbl = ("Publisher", f"{RELATORS_BASE_URL}pbl.html")
        pbd = ("Publisher director", f"{RELATORS_BASE_URL}pbd.html")
        ppt = ("Puppeteer", f"{RELATORS_BASE_URL}ppt.html")
        rcp = ("Addressee", f"{RELATORS_BASE_URL}rcp.html")
        rce = ("Recording engineer", f"{RELATORS_BASE_URL}rce.html")
        rth = ("Research team head", f"{RELATORS_BASE_URL}rth.html")
        rtm = ("Research team member", f"{RELATORS_BASE_URL}rtm.html")
        res = ("Researcher", f"{RELATORS_BASE_URL}res.html")
        rev = ("Reviewer", f"{RELATORS_BASE_URL}rev.html")
        rbr = ("Rubricator", f"{RELATORS_BASE_URL}rbr.html")
        rsp = ("Respondent", f"{RELATORS_BASE_URL}rsp.html")
        sce = ("Scenarist", f"{RELATORS_BASE_URL}sce.html")
        sad = ("Scientific advisor", f"{RELATORS_BASE_URL}sad.html")
        scr = ("Scribe", f"{RELATORS_BASE_URL}scr.html")
        scl = ("Sculptor", f"{RELATORS_BASE_URL}scl.html")
        sds = ("Sound designer", f"{RELATORS_BASE_URL}sds.html")
        sec = ("Secretary", f"{RELATORS_BASE_URL}sec.html")
        sll = ("Seller", f"{RELATORS_BASE_URL}sll.html")
        sgn = ("Signer", f"{RELATORS_BASE_URL}sgn.html")
        sng = ("Singer", f"{RELATORS_BASE_URL}sng.html")
        spn = ("Sponsor", f"{RELATORS_BASE_URL}spn.html")
        spk = ("Speaker", f"{RELATORS_BASE_URL}spk.html")
        stm = ("Stage manager", f"{RELATORS_BASE_URL}stm.html")
        swd = ("Software developer", f"{RELATORS_BASE_URL}swd.html")
        ths = ("Thesis advisor", f"{RELATORS_BASE_URL}ths.html")
        trl = ("Translator", f"{RELATORS_BASE_URL}trl.html")
        tyd = ("Type designer", f"{RELATORS_BASE_URL}tyd.html")
        tyg = ("Typographer", f"{RELATORS_BASE_URL}tyg.html")
        voc = ("Vocalist", f"Discontinued code")
        wde = ("Wood-engraver", f"{RELATORS_BASE_URL}wde.html")
        wam = ("Writer of accompanying material", f"{RELATORS_BASE_URL}wam.html")
        wit = ("Witness", f"{RELATORS_BASE_URL}wit.html")

        unknow = ("Unknown", "")

        def __init__(self, role, url):
            self._role = role
            self._url = url

        @property
        def full_name(self):
            return self._role

        @property
        def url(self):
            return self._url

    @classmethod
    def get_full_name(cls, role_code):
        try:
            return cls.LOCAuthorRoles[role_code].full_name
        except KeyError:
            return "Unknown"

    @classmethod
    def get_url(cls, role_code):
        try:
            return cls.LOCAuthorRoles[role_code].url
        except KeyError:
            return ""

    __tablename__ = "contributions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    rank: Mapped[int] = mapped_column(nullable=True)

    contributor_id: Mapped[int] = mapped_column(ForeignKey("contributors.id"))
    contributor: Mapped["app.db.models.contributor.Contributor"] = relationship(
        "app.db.models.contributor.Contributor",
        lazy="joined",
        cascade="all",
    )

    reference_id: Mapped[int] = mapped_column(ForeignKey("references.id"))
    reference: Mapped["app.db.models.reference.Reference"] = relationship(
        "app.db.models.reference.Reference",
        back_populates="contributions",
        lazy="raise",
    )

    role: Mapped[str] = mapped_column(nullable=False, index=True, default=LOCAuthorRoles.unknow.value)

    affiliations: Mapped[
        List["app.db.models.organization.Organization"]
    ] = relationship(
        "app.db.models.organization.Organization",
        secondary=affiliations_table,
        lazy="joined",
    )


# # Example usage:
# print(Contribution.LOCAuthorRoles.aut.full_name)  # Output: "Author"
# print(Contribution.LOCAuthorRoles.aut.url)  # Output: "https://id.loc.gov/vocabulary/relators/aut.html"
#
# print(Contribution.get_full_name("aut"))  # Output: "Author"
# print(Contribution.get_url("aut"))  # Output: "https://id.loc.gov/vocabulary/relators/aut.html"
