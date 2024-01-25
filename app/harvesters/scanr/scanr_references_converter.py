import re
from typing import AsyncGenerator

from app.db.daos.contributor_dao import ContributorDAO
from app.db.models.abstract import Abstract
from app.db.models.reference import Reference
from app.db.models.title import Title
from app.db.models.contribution import Contribution
from app.db.session import async_session
from app.harvesters.scanr.scanr_roles_converter import ScanrRolesConverter
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.json_harvester_raw_result import (
    JsonHarvesterRawResult as JsonRawResult,
)
from app.harvesters.exceptions.unexpected_format_exception import (
    UnexpectedFormatException,
)
from app.db.models.contributor import Contributor


class ScanrReferencesConverter(AbstractReferencesConverter):
    """
    Converts raw data from ScanR to a normalised Reference object
    """

    async def convert(self, raw_data: JsonRawResult) -> Reference:
        """
        Convert raw data from ScanR to a normalised Reference object
        :param raw_data: raw data from ScanR
        :return: Reference object
        """
        new_ref = Reference()

        json_payload = raw_data.payload

        title = json_payload["_source"].get("title")
        if title:
            new_ref.titles.extend(
                self._remove_duplicates_from_language_data(title, Title)
            )

        summary = json_payload["_source"].get("summary")
        if summary:
            new_ref.abstracts.extend(
                self._remove_duplicates_from_language_data(summary, Abstract)
            )

        contributions = json_payload["_source"].get("authors")
        if contributions:
            async for contribution in self._contributions(contributions):
                new_ref.contributions.append(contribution)

        new_ref.hash = self._hash(json_payload)
        new_ref.harvester = "scanR"
        new_ref.source_identifier = json_payload["_source"].get("id")
        return new_ref

    async def _contributions(self, contributions) -> AsyncGenerator[Contribution, None]:
        if len(contributions) > 1:
            # TODO : Add a method to handle contributor with multiple roles
            contributors_cache = {}
        async with async_session() as session:
            for rank, contribution in enumerate(contributions):
                role = contribution.get("role")
                name = contribution.get("fullName")
                identifier = contribution.get("person")

                if identifier is not None:
                    db_contributor = await ContributorDAO(
                        session
                    ).get_by_source_and_identifier(
                        source="scanr", source_identifier=identifier
                    )
                else:
                    db_contributor = await ContributorDAO(
                        session
                    ).get_by_source_and_name(source="scanr", name=name)

                if db_contributor is None:
                    db_contributor = Contributor(
                        source="scanr",
                        source_identifier=identifier,
                        name=name,
                    )
                else:
                    self._update_contributor_name(db_contributor, name)

                yield Contribution(
                    contributor=db_contributor,
                    role=ScanrRolesConverter.convert(role=role),
                    rank=rank,
                )

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

    def _remove_duplicates_from_language_data(self, language_data: dict, model_class):
        processed_items = [
            model_class(value=value, language=key)
            for key, value in language_data.items()
            if key != "default"
        ]

        default_item = language_data.get("default")

        if default_item:
            if not any(item for item in processed_items if item.value == default_item):
                processed_items.append(model_class(value=default_item, language=None))

        return processed_items

    def _hash_keys(self):
        return [
            "id",
            "title",
            "summary",
            "type",
            "productionType",
            "publicationDate",
            "domains",
            "affiliations",
            "authors",
            "externalIds",
        ]
