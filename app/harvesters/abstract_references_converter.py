import asyncio
import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, AsyncGenerator

from sqlalchemy.exc import IntegrityError

from app.db.daos.concept_dao import ConceptDAO
from app.db.daos.contributor_dao import ContributorDAO
from app.db.daos.document_type_dao import DocumentTypeDAO
from app.db.models.concept import Concept
from app.db.models.contribution import Contribution
from app.db.models.contributor import Contributor
from app.db.models.document_type import DocumentType
from app.db.models.label import Label
from app.db.models.reference import Reference
from app.db.session import async_session
from app.harvesters.abstract_harvester_raw_result import AbstractHarvesterRawResult
from app.services.concepts.concept_factory import ConceptFactory
from app.services.concepts.concept_informations import ConceptInformations
from app.services.concepts.dereferencing_error import DereferencingError


# TODO: Add a method who remove a ref from the queue if the title is missing
class AbstractReferencesConverter(ABC):
    """ "
    Abstract mother class for harvesters
    """

    ref_required_fields: list[str] = ["titles"]

    @dataclass
    class ContributionInformations:
        """
        Informations about a contribution
        """

        role: str | None = Contribution.Role.AUTHOR.value
        rank: int | None = None
        name: str | None = None
        identifier: str | None = None

    async def _contributions(
        self,
        contribution_informations: List[ContributionInformations],
        source: str,
    ) -> AsyncGenerator[Contribution, None]:
        contributors_cache = {}
        for contribution_information in contribution_informations:
            contributor_cache_key = (
                contribution_information.name,
                contribution_information.identifier,
            )
            db_contributor = contributors_cache.get(contributor_cache_key)
            if db_contributor is None:
                if contribution_information.identifier is not None:
                    db_contributor = (
                        await self._get_or_create_contributor_by_identifier(
                            source=source,
                            source_identifier=contribution_information.identifier,
                            name=contribution_information.name,
                        )
                    )
                    self._update_contributor_name(
                        db_contributor, contribution_information.name
                    )
                else:
                    db_contributor = await self._get_or_create_contributor_by_name(
                        source=source, name=contribution_information.name
                    )
                contributors_cache[contributor_cache_key] = db_contributor

            yield Contribution(
                contributor=db_contributor,
                role=contribution_information.role,
                rank=contribution_information.rank,
            )

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

    async def _get_or_create_contributor_by_name(
        self, source: str, name: str, new_attempt: bool = False
    ):
        async with async_session() as session:
            async with session.begin_nested():
                contributor = await ContributorDAO(session).get_by_source_and_name(
                    source=source, name=name
                )
                if contributor is None:
                    contributor = Contributor(
                        source=source,
                        source_identifier=None,
                        name=name,
                    )
                    session.add(contributor)
                    try:
                        await session.commit()
                    except IntegrityError as error:
                        # The concept has been created by another process,
                        # during resolution process,
                        # so rollback the current transaction
                        # and get the concept from the database
                        assert new_attempt is False, (
                            f"Unique name {name} violation "
                            "for contributor without uri cannot occur twice"
                            f" during concept creation : {error}"
                        )
                        await session.rollback()
                        contributor = await self._get_or_create_contributor_by_name(
                            source=source, name=name, new_attempt=True
                        )
        return contributor

    async def _get_or_create_contributor_by_identifier(
        self, source: str, source_identifier: str, name: str, new_attempt: bool = False
    ):
        async with async_session() as session:
            async with session.begin_nested():
                contributor = await ContributorDAO(
                    session
                ).get_by_source_and_identifier(
                    source=source, source_identifier=source_identifier
                )
                if contributor is None:
                    contributor = Contributor(
                        source=source,
                        source_identifier=source_identifier,
                        name=name,
                    )
                    session.add(contributor)
                    try:
                        await session.commit()
                    except IntegrityError as error:
                        assert new_attempt is False, (
                            f"Unique identifier {source_identifier} violation "
                            "for contributor cannot occur twice "
                            f"during concept creation : {error}"
                        )
                        await session.rollback()
                        contributor = (
                            await self._get_or_create_contributor_by_identifier(
                                source=source,
                                source_identifier=source_identifier,
                                name=name,
                                new_attempt=True,
                            )
                        )

        return contributor

    async def _get_or_create_concept_by_label(
        self, concept_informations: ConceptInformations, new_attempt: bool = False
    ):
        async with async_session() as session:
            async with session.begin_nested():
                concept = await ConceptDAO(session).get_concept_by_label_and_language(
                    label=concept_informations.label,
                    language=concept_informations.language,
                )
                if concept is None:
                    concept = Concept(uri=concept_informations.uri)
                    concept.labels.append(
                        Label(
                            value=concept_informations.label,
                            language=concept_informations.language,
                        )
                    )
                    session.add(concept)
                    try:
                        await session.commit()
                    except IntegrityError as error:
                        # The concept has been created by another process,
                        # during resolution process,
                        # so rollback the current transaction
                        # and get the concept from the database
                        assert new_attempt is False, (
                            f"Unique label {concept_informations.label} "
                            "for concept without uri violation cannot occur twice "
                            f"during concept creation : {error}"
                        )
                        await session.rollback()
                        concept = await self._get_or_create_concept_by_uri(
                            concept_informations=concept_informations
                        )
        return concept

    async def _get_or_create_concept_by_uri(
        self,
        concept_informations: ConceptInformations,
        new_attempt: bool = False,
    ):
        # Look for the concept in the database
        async with async_session() as session:
            async with session.begin_nested():
                concept = await ConceptDAO(session).get_concept_by_uri(
                    concept_informations.uri
                )
                # If the concept is not in the database, try to create it by dereferencing the uri
                if concept is None:
                    try:
                        concept = await ConceptFactory.solve(
                            concept_id=concept_informations.uri,
                            concept_source=concept_informations.source,
                        )
                    # If the dereferencing fails, create a concept with the uri and the label
                    except DereferencingError:
                        concept = Concept(uri=concept_informations.uri)
                        concept.labels.append(
                            Label(
                                value=concept_informations.label,
                                language=concept_informations.language,
                            )
                        )
                    session.add(concept)
                    try:
                        await session.commit()
                    except IntegrityError as error:
                        # The concept has been created by another process,
                        # during resolution process,
                        # so rollback the current transaction
                        # and get the concept from the database
                        assert new_attempt is False, (
                            f"Unique uri {concept_informations.uri} violation "
                            "cannot occur twice "
                            f"during concept creation : {error}"
                        )
                        await session.rollback()
                        concept = await self._get_or_create_concept_by_uri(
                            concept_informations=concept_informations
                        )
        return concept

    async def _get_or_create_concepts_by_uri(
        self,
        concept_informations: List[ConceptInformations],
    ):
        db_concepts = []
        # get all the concepts from the database in one query
        async with async_session() as session:
            db_concepts = await ConceptDAO(session).get_concepts_by_uri(
                [
                    concept_information.uri
                    for concept_information in concept_informations
                ]
            )
        concepts_dereferencing_coroutines = []
        # for each concept information, check if the concept is in the db_concepts list
        # if not, create a coroutine to dereference the concept
        for concept_information in concept_informations:
            if not any(
                concept.uri == concept_information.uri for concept in db_concepts
            ):
                concepts_dereferencing_coroutines.append(
                    self._get_or_create_concept_by_uri(
                        concept_information, new_attempt=False
                    )
                )
        # wait for all the coroutines to finish
        concepts_dereferencing_results = await asyncio.gather(
            *concepts_dereferencing_coroutines
        )
        # add the dereferenced concepts to the db_concepts list
        db_concepts.extend(concepts_dereferencing_results)
        return db_concepts

    async def _get_or_create_document_type_by_uri(
        self, uri: str, label: str | None, new_attempt: bool = False
    ):
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
                    except IntegrityError as error:
                        # The document type has been created
                        # by another process, during creation process,
                        # so rollback the current transaction
                        # and get the the document type from the database
                        assert new_attempt is False, (
                            f"Unique uri {uri} violation "
                            "cannot occur twice "
                            f"during document type creation : {error}"
                        )
                        await session.rollback()
                        document_type = await self._get_or_create_document_type_by_uri(
                            uri, label, new_attempt=True
                        )
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

    def _validate_reference(self, new_ref: Reference):
        return all(
            [bool(getattr(new_ref, field)) for field in self.ref_required_fields]
        )
