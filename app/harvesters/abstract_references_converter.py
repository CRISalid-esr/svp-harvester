import hashlib
from abc import ABC, abstractmethod

from app.db.daos.concept_dao import ConceptDAO
from app.db.daos.document_type_dao import DocumentTypeDAO
from app.db.models.concept import Concept
from app.db.models.label import Label
from app.db.models.document_type import DocumentType

from app.db.models.reference import Reference
from app.db.session import async_session
from app.harvesters.abstract_harvester_raw_result import AbstractHarvesterRawResult


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

    async def _get_or_create_concept_by_uri(self, uri: str, value: str, language: str):
        async with async_session() as session:
            concept = await ConceptDAO(session).get_concept_by_uri(uri)
        if concept is None:
            concept = Concept(uri=uri)
            concept.labels.append(Label(value=value, language=language))
        return concept

    async def _get_or_create_document_type_by_uri(self, uri: str, label: str | None):
        async with async_session() as session:
            document_type = await DocumentTypeDAO(session).get_document_type_by_uri(uri)
        if document_type is None:
            document_type = DocumentType(uri=uri, label=label)
        return document_type
