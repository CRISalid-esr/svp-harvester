from enum import Enum
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.affiliations import affiliations_table
from app.db.session import Base
from app.db.models.organization import Organization  # pylint: disable=unused-import


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

    __tablename__ = "contributions"

    id: Mapped[int] = mapped_column(primary_key=True)

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

    role: Mapped[str] = mapped_column(
        nullable=False, index=True, default=Role.AUTHOR.value
    )

    affiliations: Mapped[
        List["app.db.models.organization.Organization"]
    ] = relationship(
        "app.db.models.organization.Organization",
        secondary=affiliations_table,
        lazy="joined",
    )
