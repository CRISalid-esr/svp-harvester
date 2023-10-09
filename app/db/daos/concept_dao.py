from sqlalchemy import select

from app.db.abstract_dao import AbstractDAO
from app.db.models.concept_model import Concept
from app.db.models.label_model import Label


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
        )
        return await self.db_session.scalar(query)
