import hashlib
import re
from typing import Generator

from app.db.daos import ConceptDAO
from app.db.models import Reference, Title, Subtitle, Concept, Label
from app.db.session import async_session


class HalReferencesConverter:
    """
    Converts raw data from HAL to a normalised Reference object
    """

    async def convert(self, raw_data: dict) -> Reference:
        """
        Convert raw data from HAL to a normalised Reference object
        :param raw_data: raw data from HAL
        :return: Reference object
        """
        new_ref = Reference()
        [  # pylint: disable=expression-not-assigned
            new_ref.titles.append(title) for title in self._titles(raw_data)
        ]
        [  # pylint: disable=expression-not-assigned
            new_ref.subtitles.append(subtitle) for subtitle in self._subtitles(raw_data)
        ]
        async for subject in self._subjects(raw_data):
            # Concept from hal may be repeated, avoid duplicates
            if subject.id is None or subject.id not in list(
                map(lambda s: s.id, new_ref.subjects)
            ):
                new_ref.subjects.append(subject)

        new_ref.hash = self._hash(raw_data)
        new_ref.source_identifier = raw_data["docid"]
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

    async def _subjects(self, raw_data):
        fields = self._keys_by_pattern(pattern=r".*_keyword_s", data=raw_data)
        for field in fields:
            for value in raw_data[field]:
                yield await self._get_or_create_concept(
                    value=value, language=self._language_from_field_name(field)
                )

    async def _get_or_create_concept(self, value, language):
        async with async_session() as session:
            concept = await ConceptDAO(session).get_concept_by_label_and_language(
                value, language
            )
        if concept is None:
            concept = Concept()
            concept.labels.append(Label(value=value, language=language))
        return concept

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
