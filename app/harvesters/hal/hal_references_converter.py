import re
from typing import Generator
from loguru import logger

from app.db.models.abstract import Abstract
from app.db.models.reference_identifier import ReferenceIdentifier
from app.db.models.reference import Reference
from app.db.models.subtitle import Subtitle
from app.db.models.title import Title
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.exceptions.unexpected_format_exception import (
    UnexpectedFormatException,
)
from app.harvesters.hal.hal_document_type_converter import HalDocumentTypeConverter
from app.harvesters.hal.hal_qualitites_converter import HalQualitiesConverter
from app.harvesters.json_harvester_raw_result import (
    JsonHarvesterRawResult as JsonRawResult,
)
from app.services.concepts.concept_informations import ConceptInformations


class HalReferencesConverter(AbstractReferencesConverter):
    """
    Converts raw data from HAL to a normalised Reference object
    """

    @AbstractReferencesConverter.validate_reference
    async def convert(self, raw_data: JsonRawResult) -> Reference:
        """
        Convert raw data from HAL to a normalised Reference object
        :param raw_data: raw data from HAL
        :return: Reference object
        """
        json_payload = raw_data.payload
        new_ref = Reference()
        [  # pylint: disable=expression-not-assigned
            new_ref.identifiers.append(identifier)
            for identifier in self._identifiers(json_payload)
        ]

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
        new_ref.document_type.append(await self._document_type(json_payload))
        async for subject in self._concepts(json_payload):
            # Concept from hal may be repeated, avoid duplicates
            if subject.id is None or subject.id not in list(
                map(lambda s: s.id, new_ref.subjects)
            ):
                new_ref.subjects.append(subject)
        await self._add_contributions(json_payload, new_ref)

        new_ref.hash = self._hash(json_payload)
        new_ref.harvester = "hal"
        new_ref.source_identifier = raw_data.source_identifier
        return new_ref

    def _identifiers(self, raw_data):
        fields = self._keys_by_pattern(pattern=r".*Id_s", data=raw_data)
        for field in fields:
            # Identifier that are list: europeanProjectCallId_s, wosId_s, piiId_s, pubmedcentralId_s
            if isinstance(raw_data[field], list):
                for value in raw_data[field]:
                    yield ReferenceIdentifier(type=field, value=value)
            else:
                yield ReferenceIdentifier(type=field, value=raw_data[field])

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

    async def _concepts(self, raw_data):
        fields = raw_data.get("jel_s", [])
        # If we have jel_s fields, we use them as subjects
        for code in fields:
            try:
                yield await self._get_or_create_concept_by_uri(
                    ConceptInformations(
                        uri=code,
                        source=ConceptInformations.ConceptSources.JEL,
                    )
                )
            except AssertionError:
                logger.error(f"Could not create concept with uri {code}")
                continue
        fields = self._keys_by_pattern(pattern=r".*_keyword_s", data=raw_data)
        for field in fields:
            for label in raw_data[field]:
                yield await self._get_or_create_concept_by_label(
                    ConceptInformations(
                        label=label, language=self._language_from_field_name(field)
                    )
                )

    async def _add_contributions(self, raw_data: dict, new_ref: Reference) -> None:
        if len(raw_data.get("authQuality_s", [])) != len(
            raw_data.get("authFullNameFormIDPersonIDIDHal_fs", [])
        ):
            raise UnexpectedFormatException(
                "Number of qualities and contributors "
                f"is not the same for halId_s: {raw_data['halId_s']}"
            )
        contribution_informations = []
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
            contribution_informations.append(
                AbstractReferencesConverter.ContributionInformations(
                    role=HalQualitiesConverter.convert(quality),
                    identifier=id_hal if id_hal != "0" else None,
                    name=name,
                    rank=rank,
                )
            )
        async for contribution in self._contributions(
            contribution_informations=contribution_informations, source="hal"
        ):
            new_ref.contributions.append(contribution)

    async def _document_type(self, raw_data):
        code_document_type = raw_data.get("docType_s", None)
        uri, label = HalDocumentTypeConverter().convert(code_document_type)
        return await self._get_or_create_document_type_by_uri(uri, label)

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
