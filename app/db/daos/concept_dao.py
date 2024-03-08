from sqlalchemy import select
from sqlalchemy.orm import raiseload, joinedload

from app.db.abstract_dao import AbstractDAO
from app.db.models.concept import Concept
from app.db.models.label import Label


class ConceptDAO(AbstractDAO):
    """
    Data access object for concepts
    """

    async def get_concept_by_label_and_language(
        self, label: str, language: str
    ) -> Concept | None:
        """
        Get a concept by its label and language

        :param label: label of the concept
        :param language: language of the concept
        :return: the concept or None if not found
        """
        query = (
            select(Concept)
            .join(Label)
            .where(Label.value == label, Label.language == language)
            .options(raiseload("*"))
        )
        return await self.db_session.scalar(query)

    async def get_concept_by_uri(self, uri: str) -> Concept | None:
        """
        Get a concept by its uri

        :param uri: uri of the concept
        :return: the concept or None if not found
        """
        query = (
            select(Concept)
            .where(Concept.uri == uri)
            .options(raiseload("*"))
            .options(joinedload(Concept.labels))
        )
        return await self.db_session.scalar(query)

    async def get_concepts_by_uri(self, uris: list[str]) -> list[Concept]:
        """
        Get a list of concepts by their uris

        :param uris: uris of the concepts
        :return: the list of concepts
        """
        query = select(Concept).where(Concept.uri.in_(uris)).options(raiseload("*"))
        return (await self.db_session.execute(query)).unique().scalars().all()
