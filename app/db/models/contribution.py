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

        AUTHOR = "Author"
        ANALYST = "Analyst"
        CORRESPONDENT_AUTHOR = "Correspondent Author"
        CONTRIBUTOR = "Contributor"
        ANNOTATOR = "Annotator"
        COMPILER = "Compiler"
        COMPOSER = "Composer"
        CARTOGRAPHER = "Cartographer"
        CONTRACTOR = "Contractor"
        COMMENTATOR_OF_WRITTEN_TEXT = "Commentator Of Written Text"
        DESIGNER = "Designer"
        DISSERTANT = "Dissertant"
        EDITOR = "Editor"
        FILM_DIRECTOR = "Film Director"
        FILM_EDITOR = "Film Editor"
        SCIENTIFIC_EDITOR = "Scientific Editor"
        ILLUSTRATOR = "Illustrator"
        TRANSLATOR = "Translator"
        INTERVIEWEE = "Interviewee"
        INTERVIEWER = "Interviewer"
        AUTHOR_OF_INTRODUCTION = "Author Of Introduction"
        SPEAKER = "Speaker"
        DEGREE_COMMITTEE_MEMBER = "Degree Committee Member"
        THESIS_ADVISOR = "Thesis Advisor"
        ARCHITECT = "Architect"
        ARTISTIC_DIRECTOR = "Artistic Director"
        SOFTWARE_DEVELOPER = "Software Developer"
        PHOTOGRAPHER = "Photographer"
        PRODUCER = "Producer"
        PROJECT_DIRECTOR = "Project Director"
        PRODUCTION_PERSONNEL = "Production Personnel"
        SCIENTIFIC_ADVISOR = "Scientific Advisor"
        SOUND_DESIGNER = "Sound Designer"
        STAGE_MANAGER = "Stage Manager"
        WRITER_OF_ACCOMPANYING_MATERIAL = "Writer Of Accompanying Material"
        WRITER_OF_INTRODUCTION = "Writer Of Introduction"
        WITNESS = "Witness"
        OTHER = "Other"
        RESPONDANT = "Respondant"
        UNKNOWN = "Unknown"

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
