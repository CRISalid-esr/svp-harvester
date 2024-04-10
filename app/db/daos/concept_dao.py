from sqlalchemy import select
from sqlalchemy.sql.expression import func

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

    # pylint: disable=singleton-comparison
    async def get_random_concept_not_dereferenced(
        self, exclude_ids: list[int] = None
    ) -> Concept | None:
        """
        Get a random concept that has not been dereferenced yet
        It need to have an uri to be dereferenced

        :param exclude_ids: We can provide a list of ids to exclude

        :return: the Concept or None if not found
        """
        if exclude_ids is None:
            exclude_ids = []

        query = (
            select(Concept)
            .where(Concept.dereferenced == False)
            .where(Concept.uri != None)
            .where(~Concept.id.in_(exclude_ids))
            .order_by(func.random())  # pylint: disable=not-callable
            .limit(1)
        )

        return await self.db_session.scalar(query)
