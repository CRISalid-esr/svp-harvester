from typing import AsyncGenerator
from app.db.daos.contributor_dao import ContributorDAO
from app.db.models.concept import Concept

from app.db.models.contribution import Contribution
from app.db.models.contributor import Contributor
from app.db.models.title import Title
from app.db.models.reference import Reference
from app.db.models.abstract import Abstract
from app.db.session import async_session

from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.json_harvester_raw_result import JsonHarvesterRawResult
from app.harvesters.open_alex.open_alex_document_type_converter import (
    OpenAlexDocumentTypeConverter,
)


class OpenAlexReferencesConverter(AbstractReferencesConverter):
    """
    Converts raw data from OpenAlex to a normalised Reference object
    """

    async def convert(self, raw_data: JsonHarvesterRawResult) -> Reference:
        """
        Convert raw data from OpenAlex to a normalised Reference object
        :param raw_data: raw data from OpenAlex
        :return: Reference object
        """
        json_payload = raw_data.payload
        new_ref = Reference()

        language = json_payload.get("language", None)
        new_ref.titles.append(self._title(json_payload, language))
        abstract = self._abstract(json_payload, language)
        if abstract is not None:
            new_ref.abstracts.append(abstract)
        new_ref.document_type.append(await self._document_type(json_payload))

        async for contribution in self._contributions(json_payload):
            new_ref.contributions.append(contribution)

        async for concept in self._concepts(json_payload, language):
            new_ref.subjects.append(concept)

        new_ref.source_identifier = raw_data.source_identifier
        new_ref.hash = self._hash(json_payload)
        return new_ref

    async def _concepts(self, json_payload, language) -> AsyncGenerator[Concept, None]:
        concept_cache = {}

        for concept in self._value_from_key(json_payload, "concepts", []):
            uri = concept.get("wikidata")
            label = concept.get("display_name")
            concept_key = uri

            if concept_key in concept_cache:
                yield concept_cache[concept_key]
                continue
            concept_db = await self._get_or_create_concept_by_uri(uri, label, language)
            concept_cache[concept_key] = concept_db
            yield concept_db

    def _title(self, json_payload, language: str):
        return Title(
            value=self._value_from_key(json_payload, "title"), language=language
        )

    def _abstract(self, json_payload, language: str):
        abstract = self._value_from_key(json_payload, "abstract_inverted_index")
        if abstract is None:
            return None
        value = " ".join(abstract.keys())
        return Abstract(value=value, language=language)

    async def _document_type(self, json_payload):
        document_type = self._value_from_key(json_payload, "type")
        uri, label = OpenAlexDocumentTypeConverter().convert(document_type)
        return await self._get_or_create_document_type_by_uri(uri, label)

    async def _contributions(self, json_payload) -> AsyncGenerator[Contribution, None]:
        contributors_cache = {}

        async with async_session() as session:
            for author_object in self._value_from_key(
                json_payload, "authorships", default=[]
            ):
                author = author_object.get("author")
                name = author.get("display_name")
                id_open_alex = author.get("id")

                contributor_key = (name, id_open_alex)

                db_contributor = contributors_cache.get(contributor_key, None)

                if db_contributor is None:
                    if id_open_alex:
                        db_contributor = await ContributorDAO(
                            session
                        ).get_by_source_and_identifier(
                            source="open_alex", source_identifier=id_open_alex
                        )
                    else:
                        db_contributor = await ContributorDAO(
                            session
                        ).get_by_source_and_name(source="open_alex", name=name)
                    if db_contributor is None:
                        db_contributor = Contributor(
                            source="open_alex",
                            source_identifier=id_open_alex,
                            name=name,
                        )
                    contributors_cache[contributor_key] = db_contributor

                # TODO Rank and role? Open Alex give author position (first, middle, last)
                yield Contribution(
                    contributor=db_contributor,
                )

    def _value_from_key(self, json_payload, key: str, default=None):
        return json_payload.get(key, default)

    def _hash_keys(self) -> list[str]:
        return [
            "id",
            "title",
            "type",
        ]
