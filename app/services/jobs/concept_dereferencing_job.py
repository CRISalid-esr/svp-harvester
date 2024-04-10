from loguru import logger
from app.db.daos.concept_dao import ConceptDAO
from app.services.concepts.concept_factory import ConceptFactory
from app.services.concepts.concept_informations import ConceptInformations
from app.services.concepts.dereferencing_error import DereferencingError
from app.services.jobs.abstract_offline_job import AbstractOfflineJob
from app.db.session import async_session


class ConceptDereferencingJob(AbstractOfflineJob):
    """
    Job for dereferencing concepts.
    """

    async def run(self):
        """
        Try to dereference all concepts that have not been dereferenced yet.
        """
        async with async_session() as session:
            concept = await ConceptDAO(session).get_random_concept_not_dereferenced()
            if concept is None:
                return

            already_seen = set()

            while concept:
                already_seen.add(concept.id)
                try:
                    concept_informations = ConceptInformations(uri=concept.uri)
                    ConceptFactory.complete_information(concept_informations)
                    concept_deferenced = await ConceptFactory.solve(
                        concept_informations
                    )
                    concept_deferenced.id = concept.id
                    await session.merge(concept_deferenced)
                    await session.commit()
                    concept = await ConceptDAO(
                        session
                    ).get_random_concept_not_dereferenced()
                except DereferencingError as e:
                    logger.error(f"Error while dereferencing concept {concept}: {e}")
                concept = await ConceptDAO(session).get_random_concept_not_dereferenced(
                    exclude_ids=already_seen
                )
