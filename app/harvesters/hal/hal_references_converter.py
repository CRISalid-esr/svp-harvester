import re
from typing import Generator, AsyncGenerator

from app.db.daos.contributor_dao import ContributorDAO
from app.db.models.abstract import Abstract
from app.db.models.contribution import Contribution
from app.db.models.contributor import Contributor
from app.db.models.reference import Reference
from app.db.models.title import Title
from app.db.models.subtitle import Subtitle
from app.db.session import async_session
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.exceptions.unexpected_format_exception import (
    UnexpectedFormatException,
)
from app.harvesters.hal.hal_qualitites_converter import HalQualitiesConverter
from app.harvesters.json_harvester_raw_result import (
    JsonHarvesterRawResult as JsonRawResult,
)


class HalReferencesConverter(AbstractReferencesConverter):
    """
    Converts raw data from HAL to a normalised Reference object
    """

    async def convert(self, raw_data: JsonRawResult) -> Reference:
        """
        Convert raw data from HAL to a normalised Reference object
        :param raw_data: raw data from HAL
        :return: Reference object
        """
        json_payload = raw_data.payload
        new_ref = Reference()
        [  # pylint: disable=expression-not-assigned
            new_ref.titles.append(title) for title in self._titles(json_payload)
        ]
        [  # pylint: disable=expression-not-assigned
            new_ref.subtitles.append(subtitle)
            for subtitle in self._subtitles(json_payload)
        ]
        [  # pylint: disable=expression-not-assigned
            new_ref.abstracts.append(abstract)
            for abstract in self._abstracts(json_payload)
        ]
        async for subject in self._subjects(json_payload):
            # Concept from hal may be repeated, avoid duplicates
            if subject.id is None or subject.id not in list(
                map(lambda s: s.id, new_ref.subjects)
            ):
                new_ref.subjects.append(subject)
        async for contribution in self._contributions(json_payload):
            new_ref.contributions.append(contribution)
        new_ref.hash = self._hash(json_payload)
        new_ref.harvester = "hal"
        new_ref.source_identifier = raw_data.source_identifier
        return new_ref

    def _titles(self, raw_data):
        for value, language in self._values_from_field_pattern(
            r".*_title_s$", raw_data
        ):
            yield Title(value=value, language=language)

    def _subtitles(self, raw_data):
        for value, language in self._values_from_field_pattern(
            r".*_subTitle_s$", raw_data
        ):
            yield Subtitle(value=value, language=language)

    def _abstracts(self, raw_data):
        for value, language in self._values_from_field_pattern(
            r".*_abstract_s$", raw_data
        ):
            yield Abstract(value=value, language=language)

    async def _subjects(self, raw_data):
        fields = self._keys_by_pattern(pattern=r".*_keyword_s", data=raw_data)
        for field in fields:
            for value in raw_data[field]:
                yield await self._get_or_create_concept_by_label(
                    value=value, language=self._language_from_field_name(field)
                )

    async def _contributions(self, raw_data) -> AsyncGenerator[Contribution, None]:
        if len(raw_data.get("authQuality_s", [])) != len(
            raw_data.get("authFullNameFormIDPersonIDIDHal_fs", [])
        ):
            raise UnexpectedFormatException(
                "Number of qualities and contributors "
                f"is not the same for docid: {raw_data['docid']}"
            )

        async with async_session() as session:
            # Open transaction as contributions resolution may update some of the contributors
            for rank, contribution in enumerate(
                zip(
                    raw_data.get("authQuality_s", []),
                    raw_data.get("authFullNameFormIDPersonIDIDHal_fs", []),
                )
            ):
                quality, contributor = contribution
                if not re.match(r".*_FacetSep_.*-.*_FacetSep_", contributor):
                    raise UnexpectedFormatException(
                        f"Unexpected format for contributor {contributor}"
                    )
                name, ids, _ = contributor.split("_FacetSep_")
                _, id_hal = ids.split("-")
                # if IdHal is not '0', find the contributor by source/identifier,
                # else find the contributor by source/ name
                db_contributor = None
                if id_hal != "0":
                    db_contributor = await ContributorDAO(
                        session
                    ).get_by_source_and_identifier(
                        source="hal", source_identifier=id_hal
                    )
                else:
                    db_contributor = await ContributorDAO(
                        session
                    ).get_by_source_and_name(source="hal", name=name)
                if db_contributor is None:
                    db_contributor = Contributor(
                        source="hal",
                        source_identifier=None if id_hal == "0" else id_hal,
                        name=name,
                    )
                else:
                    self._update_contributor_name(db_contributor, name)

                yield Contribution(
                    contributor=db_contributor,
                    role=HalQualitiesConverter.convert(quality=quality),
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

    def _hash_keys(self):
        return [
            "docid",
            "citationRef_s",
            "citationFull_s",
            "en_title_s",
            "en_keyword_s",
            "en_abstract_s",
            "authIdForm_i",
            "authFullNameFormIDPersonIDIDHal_fs",
            "authIdHasStructure_fs",
            "labStructId_i",
            "docType_s",
            "publicationDate_tdate",
        ]

    def _keys_by_pattern(self, pattern: str, data: dict) -> list[str]:
        """
        Return a list of keys from a result dict matching a pattern
        :param pattern: the pattern to match
        :param data: the dict to search in
        :return: a list of keys
        """
        reg_exp = re.compile(pattern)
        return list(filter(reg_exp.match, data.keys()))

    def _values_from_field_pattern(
        self, pattern: str, raw_data: dict
    ) -> Generator[Title, None, None]:
        fields = self._keys_by_pattern(pattern=pattern, data=raw_data)
        for field in fields:
            for value in raw_data[field]:
                yield (value, self._language_from_field_name(field))

    def _language_from_field_name(self, multilang_field_name):
        """
        Extract language code from Hal multilang field name
        :param multilang_field_name: Hal multilang field name
        :return: 2 letters language code
        """
        return multilang_field_name.split("_")[0]
