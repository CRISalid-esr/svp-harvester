# TODO: Check if it"s possible to make a generic converter for all roles
#  => Make a base enum role based on loc roles.
#  If a role is not in known LOC roles, it gonna be analized by the child class and treated.
#  => In case it"s not treated, it will be considered as unknown and a warning will be raised.

from abc import ABC
from enum import Enum

# Define base LOC URL
RELATORS_BASE_URL = "https://id.loc.gov/vocabulary/relators/"


class AbstractRolesConverter(ABC):
    """
    Abstract mother class for all roles converters.
    """

    class LOCAuthorRoles(Enum):

        act = ("Actor", f"{RELATORS_BASE_URL}act.html")
        adp = ("Adapter", f"{RELATORS_BASE_URL}adp.html")
        anm = ("Animator", f"{RELATORS_BASE_URL}anm.html")
        ant = ("Bibliographic antecedent", f"{RELATORS_BASE_URL}ant.html")
        ann = ("Annotator", f"{RELATORS_BASE_URL}ann.html")
        arr = ("Arranger", f"{RELATORS_BASE_URL}arr.html")
        art = ("Artist", f"{RELATORS_BASE_URL}art.html")
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
        drt = ("Director", f"{RELATORS_BASE_URL}drt.html")
        dst = ("Distributor", f"{RELATORS_BASE_URL}dst.html")
        dnr = ("Donor", f"{RELATORS_BASE_URL}dnr.html")
        dub = ("Dubious author", f"{RELATORS_BASE_URL}dub.html")
        edt = ("Editor", f"{RELATORS_BASE_URL}edt.html")
        egr = ("Engraver", f"{RELATORS_BASE_URL}egr.html")
        etr = ("Etcher", f"{RELATORS_BASE_URL}etr.html")
        exp = ("Expert", f"{RELATORS_BASE_URL}exp.html")
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
        sce = ("Scenarist", f"{RELATORS_BASE_URL}sce.html")
        sad = ("Scientific advisor", f"{RELATORS_BASE_URL}sad.html")
        scr = ("Scribe", f"{RELATORS_BASE_URL}scr.html")
        scl = ("Sculptor", f"{RELATORS_BASE_URL}scl.html")
        sec = ("Secretary", f"{RELATORS_BASE_URL}sec.html")
        sll = ("Seller", f"{RELATORS_BASE_URL}sll.html")
        sgn = ("Signer", f"{RELATORS_BASE_URL}sgn.html")
        sng = ("Singer", f"{RELATORS_BASE_URL}sng.html")
        spn = ("Sponsor", f"{RELATORS_BASE_URL}spn.html")
        stm = ("Stage manager", f"{RELATORS_BASE_URL}stm.html")
        ths = ("Thesis advisor", f"{RELATORS_BASE_URL}ths.html")
        trl = ("Translator", f"{RELATORS_BASE_URL}trl.html")
        tyd = ("Type designer", f"{RELATORS_BASE_URL}tyd.html")
        tyg = ("Typographer", f"{RELATORS_BASE_URL}tyg.html")
        voc = ("Vocalist", f"Discontinued code")
        wde = ("Wood-engraver", f"{RELATORS_BASE_URL}wde.html")
        wam = ("Writer of accompanying material", f"{RELATORS_BASE_URL}wam.html")

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


# # Example usage:
print(AbstractRolesConverter.LOCAuthorRoles.aut.full_name)  # Output: "Author"
print(AbstractRolesConverter.LOCAuthorRoles.aut.url)  # Output: "https://id.loc.gov/vocabulary/relators/aut.html"

print(AbstractRolesConverter.get_full_name("aut"))  # Output: "Author"
print(AbstractRolesConverter.get_url("aut"))  # Output: "https://id.loc.gov/vocabulary/relators/aut.html"