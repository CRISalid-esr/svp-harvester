import asyncio
import hashlib
from abc import ABC, abstractmethod
from typing import List, Dict

from sqlalchemy.exc import IntegrityError

from app.db.daos.concept_dao import ConceptDAO
from app.db.daos.document_type_dao import DocumentTypeDAO
from app.db.models.concept import Concept
from app.db.models.contributor import Contributor
from app.db.models.label import Label
from app.db.models.document_type import DocumentType

from app.db.models.reference import Reference
from app.db.session import async_session
from app.harvesters.abstract_harvester_raw_result import AbstractHarvesterRawResult
from app.services.concepts.concept_factory import ConceptFactory
from app.services.concepts.dereferencing_error import DereferencingError


class AbstractReferencesConverter(ABC):
    """ "
    Abstract mother class for harvesters
    """

    @abstractmethod
    async def convert(self, raw_data: AbstractHarvesterRawResult) -> Reference:
        """
        Converts raw data from harvester source to a Normalised Reference object
        :param raw_data: Raw data from harvester source
        :return: Normalised Reference object
        """

    def _hash(self, raw_data: dict):
        reduced_dic: dict = dict(
            zip(
                self._hash_keys(),
                [raw_data[k] for k in self._hash_keys() if k in raw_data],
            )
        )
        string_to_hash = ""
        for values in reduced_dic.values():
            if isinstance(values, list):
                string_to_hash += ",".join((str(value) for value in values))
            else:
                string_to_hash += str(values)
        return hashlib.sha256(string_to_hash.encode()).hexdigest()

    def _hash_keys(self) -> list[str]:
        raise NotImplementedError

    async def _get_or_create_concept_by_label(self, value: str, language: str):
        async with async_session() as session:
            concept = await ConceptDAO(session).get_concept_by_label_and_language(
                value, language
            )
        if concept is None:
            concept = Concept()
            concept.labels.append(Label(value=value, language=language))
        return concept

    async def _get_or_create_concept_by_uri(
        self,
        uri: str,
        value: str,
        language: str,
        concept_source: ConceptFactory.ConceptSources | None = None,
    ):
        # Look for the concept in the database
        async with async_session() as session:
            async with session.begin_nested():
                concept = await ConceptDAO(session).get_concept_by_uri(uri)
                # If the concept is not in the database, try to create it by dereferencing the uri
                if concept is None:
                    try:
                        concept = await ConceptFactory.solve(
                            concept_id=uri, concept_source=concept_source
                        )
                    # If the dereferencing fails, create a concept with the uri and the label
                    except DereferencingError:
                        concept = Concept(uri=uri)
                        concept.labels.append(Label(value=value, language=language))
                    session.add(concept)
                    try:
                        await session.commit()
                    except IntegrityError:
                        await session.rollback()
                        concept = await ConceptDAO(session).get_concept_by_uri(uri)

                return concept

    async def _get_or_create_concepts_by_uri(
        self,
        concept_informations: List[
            Dict[str, str | ConceptFactory.ConceptSources | None]
        ],
    ):
        db_concepts = []
        # get all the concepts from the database in one query
        async with async_session() as session:
            db_concepts = await ConceptDAO(session).get_concepts_by_uri(
                [
                    concept_information["uri"]
                    for concept_information in concept_informations
                ]
            )
        concepts_dereferencing_coroutines = []
        # for each concept information, check if the concept is in the db_concepts list
        # if not, create a coroutine to dereference the concept
        for concept_information in concept_informations:
            if not any(
                concept.uri == concept_information["uri"] for concept in db_concepts
            ):
                concepts_dereferencing_coroutines.append(
                    self._get_or_create_concept_by_uri(
                        concept_information["uri"],
                        concept_information.get("label", None),
                        concept_information.get("language", None),
                        concept_information.get("concept_source", None),
                    )
                )
        # wait for all the coroutines to finish
        concepts_dereferencing_results = await asyncio.gather(
            *concepts_dereferencing_coroutines
        )
        # add the dereferenced concepts to the db_concepts list
        db_concepts.extend(concepts_dereferencing_results)
        return db_concepts

    async def _get_or_create_document_type_by_uri(self, uri: str, label: str | None):
        async with async_session() as session:
            async with session.begin_nested():
                document_type = await DocumentTypeDAO(session).get_document_type_by_uri(
                    uri
                )
                if document_type is None:
                    document_type = DocumentType(uri=uri, label=label)
                    session.add(document_type)
                    try:
                        await session.commit()
                    except IntegrityError:
                        await session.rollback()
                        document_type = await DocumentTypeDAO(
                            session
                        ).get_document_type_by_uri(uri)
        return document_type

    def _update_contributor_name(self, db_contributor: Contributor, name: str):
        """
        Updates the name of the contributor if it is different from the one in the database
        and stores the old name in the name_variants field

        :param db_contributor:
        :param name: new name received from hal
        :return: None
        """
        if db_contributor.name == name:
            return
        if db_contributor.name not in db_contributor.name_variants:
            # with append method sqlalchemy would not detect the change
            db_contributor.name_variants = db_contributor.name_variants + [
                db_contributor.name
            ]
        db_contributor.name = name
