import re
from typing import Generator, Set

from loguru import logger
from pydantic import ValidationError
from semver import Version

from app.db.models.abstract import Abstract
from app.db.models.book import Book
from app.db.models.journal import Journal
from app.db.models.reference import Reference
from app.db.models.reference_identifier import ReferenceIdentifier
from app.db.models.reference_manifestation import ReferenceManifestation
from app.db.models.subtitle import Subtitle
from app.db.models.title import Title
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.exceptions.unexpected_format_exception import (
    UnexpectedFormatException,
)
from app.harvesters.hal.hal_custom_metadata_schema import HalCustomMetadataSchema
from app.harvesters.hal.hal_document_type_converter import HalDocumentTypeConverter
from app.harvesters.hal.hal_roles_converter import HalRolesConverter
from app.harvesters.hal.hal_tei_interface import HalTEIDecoder
from app.harvesters.json_harvester_raw_result import (
    JsonHarvesterRawResult as JsonRawResult,
)
from app.services.book.book_data_class import BookInformations
from app.services.concepts.concept_informations import ConceptInformations
from app.services.hash.hash_key import HashKey
from app.services.issue.issue_data_class import IssueInformations
from app.services.journal.journal_data_class import JournalInformations
from app.services.organizations.organization_informations import (
    OrganizationInformations,
)
from app.utilities.date_utilities import check_valid_iso8601_date
from app.utilities.isbn_utilities import get_isbns


class HalReferencesConverter(AbstractReferencesConverter):
    """
    Converts raw data from HAL to a normalised Reference object
    """

    FIELD_NAME_TO_IDENTIFIER_TYPE: dict[str, str] = {
        "arxivId_s": ReferenceIdentifier.IdentifierType.ARXIV.value,
        "bibcodeId_s": ReferenceIdentifier.IdentifierType.BIBCODE.value,
        "biorxivId_s": ReferenceIdentifier.IdentifierType.BIORXIV.value,
        "cernId_s": ReferenceIdentifier.IdentifierType.CERN.value,
        "chemrxivId_s": ReferenceIdentifier.IdentifierType.CHEMRXIV.value,
        "doiId_s": ReferenceIdentifier.IdentifierType.DOI.value,
        "ensamId_s": ReferenceIdentifier.IdentifierType.ENSAM.value,
        "halId_s": ReferenceIdentifier.IdentifierType.HAL.value,
        "inerisId_s": ReferenceIdentifier.IdentifierType.INERIS.value,
        "inspireId_s": ReferenceIdentifier.IdentifierType.INSPIRE.value,
        "irdId_s": ReferenceIdentifier.IdentifierType.IRD.value,
        "irsteaId_s": ReferenceIdentifier.IdentifierType.IRSTEA.value,
        "irThesaurusId_s": ReferenceIdentifier.IdentifierType.IRTHESAURUS.value,
        "meditagriId_s": ReferenceIdentifier.IdentifierType.MEDITAGRI.value,
        "nntId_s": ReferenceIdentifier.IdentifierType.NNT.value,
        "okinaId_s": ReferenceIdentifier.IdentifierType.OKINA.value,
        "oataoId_s": ReferenceIdentifier.IdentifierType.OATAO.value,
        "piiId_s": ReferenceIdentifier.IdentifierType.PII.value,
        "ppnId_s": ReferenceIdentifier.IdentifierType.PPN.value,
        "prodinraId_s": ReferenceIdentifier.IdentifierType.PRODINRA.value,
        "pubmedId_s": ReferenceIdentifier.IdentifierType.PMID.value,
        "pubmedcentralId_s": ReferenceIdentifier.IdentifierType.PUBMEDCENTRAL.value,
        "sciencespoId_s": ReferenceIdentifier.IdentifierType.SCIENCESPO.value,
        "swhidId_s": ReferenceIdentifier.IdentifierType.SWHID.value,
        "wosId_s": ReferenceIdentifier.IdentifierType.WOS.value,
    }

    @AbstractReferencesConverter.validate_reference
    async def convert(self, raw_data: JsonRawResult, new_ref: Reference) -> None:
        """
        Convert raw data from HAL to a normalised Reference object
        :param raw_data: raw data from HAL
        :param new_ref: Reference object
        :return: None
        """
        json_payload = raw_data.payload
        tei_decoder = self._build_tei_decoder(json_payload)

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

        document_types_from_payload = set(
            json_payload.get(document_type)
            for document_type in ("docType_s", "docSubType_s")
        )
        document_types_from_payload.discard(None)
        document_types_from_payload.discard("NULL")

        for document_type in document_types_from_payload:
            validated_document_type = await self._document_type(document_type)
            new_ref.document_type.append(validated_document_type)

        async for subject in self._concepts(json_payload):
            # Concept from hal may be repeated, avoid duplicates
            if subject.id is None or subject.id not in list(
                map(lambda s: s.id, new_ref.subjects)
            ):
                new_ref.subjects.append(subject)

        await self._add_contributions(json_payload, new_ref, tei_decoder)

        self._add_hal_manifestation(json_payload, new_ref)

        self._add_issued_date(json_payload, new_ref)

        self._add_created_date(json_payload, new_ref)

        self._add_hal_collection_codes(json_payload, new_ref)

        self._add_hal_submit_type(json_payload, new_ref)

        new_ref.page = json_payload.get("page_s", None)
        journal = await self._journal(json_payload)

        if journal:
            issue = await self._issue(json_payload, journal)
            new_ref.issue = issue

        if ("Book" in [dc.label for dc in new_ref.document_type]) or (
            "Chapter" in [dc.label for dc in new_ref.document_type]
        ):
            book = await self._book(raw_data.payload)
            if book:
                new_ref.book = book

        await self._add_organization(json_payload, new_ref)

    def _build_tei_decoder(self, json_payload):
        tei_decoder = None
        tei_payload = json_payload.get("label_xml", None)
        if tei_payload:
            tei_decoder = HalTEIDecoder(tei_raw_data=tei_payload)
        return tei_decoder

    def _add_created_date(self, json_payload, new_ref):
        try:
            new_ref.created = check_valid_iso8601_date(
                json_payload.get("producedDate_tdate", None)
            )
        except UnexpectedFormatException as error:
            logger.error(
                f"Hal reference converter cannot create created date from producedDate_tdate in"
                f" {json_payload['halId_s']}: {error}"
            )

    def _add_issued_date(self, json_payload, new_ref):
        try:
            new_ref.raw_issued = json_payload.get("publicationDate_s", None)
            new_ref.issued = check_valid_iso8601_date(
                json_payload.get("publicationDate_tdate", None)
            )
        except UnexpectedFormatException as error:
            logger.error(
                f"Hal reference converter cannot create issued date from publicationDate_tdate in"
                f" {json_payload['halId_s']}: {error}"
            )

    @staticmethod
    def _add_hal_collection_codes(json_payload: dict, new_ref):
        """
        Extract HAL collection codes and set them in custom_metadata.
        Ensures proper formatting and logs validation errors.
        """
        collection_codes = json_payload.get("collCode_s", [])
        if isinstance(collection_codes, str):
            collection_codes = [collection_codes]

        custom_metadata = new_ref.custom_metadata or {}

        try:
            updated_metadata = HalCustomMetadataSchema(
                **{**custom_metadata, "hal_collection_codes": collection_codes}
            )
            new_ref.custom_metadata = updated_metadata.model_dump()
        except ValidationError as e:
            logger.warning(
                "Invalid HAL custom metadata for reference %s: %s",
                new_ref.source_identifier,
                e.json(),
            )

    @staticmethod
    def _add_hal_submit_type(json_payload: dict, new_ref: Reference) -> None:
        """
        Extract and validate the HAL submit type from payload, if present.
        Sets one of: 'notice', 'file', 'annex' into new_ref.custom_metadata.
        """
        raw_value = json_payload.get("submitType_s")
        if raw_value is None:
            return

        try:
            submit_type = HalCustomMetadataSchema.HalSubmitType(raw_value)
        except ValueError:
            logger.warning(
                "Invalid halSubmitType_s: '%s' in HAL payload %s",
                raw_value,
                json_payload.get("halId_s"),
            )
            return

        custom_metadata = new_ref.custom_metadata or {}
        try:
            updated_metadata = HalCustomMetadataSchema(
                **{**custom_metadata, "hal_submit_type": submit_type}
            )
            new_ref.custom_metadata = updated_metadata.model_dump()
        except ValidationError as e:
            logger.warning(
                "Validation error in HAL custom metadata for HAL ID %s: %s",
                json_payload.get("halId_s"),
                e.json(),
            )

    async def _book(self, raw_data) -> Book | None:
        title = raw_data.get("bookTitle_s", None)
        publisher = raw_data.get("publisher_s", None)
        if isinstance(publisher, list):
            publisher = publisher[0]
        isbn = raw_data.get("isbn_s", None)
        isbn10, isbn13 = get_isbns(isbn)
        if (title is None) and (isbn is None):
            return None
        return await self._get_or_create_book(
            BookInformations(
                title=title,
                source=self._get_source(),
                publisher=publisher,
                isbn10=isbn10,
                isbn13=isbn13,
            )
        )

    async def _journal(self, raw_data) -> Journal | None:
        title = raw_data.get("journalTitle_s", None)
        issn = raw_data.get("journalIssn_s", None)
        eissn = raw_data.get("journalEissn_s", None)
        publisher = raw_data.get("journalPublisher_s", None)
        source_identifier = raw_data.get("journalId_i", None)
        if source_identifier is None:
            return None
        journal = await self._get_or_create_journal(
            JournalInformations(
                source=self._get_source(),
                source_identifier=str(source_identifier),
                eissn=[eissn] if eissn is not None else [],
                issn=[issn] if issn is not None else [],
                publisher=publisher,
                titles=[title],
            )
        )
        if publisher is not None and journal.publisher is None:
            journal.publisher = publisher
        if title is not None and (title not in journal.titles):
            journal.titles.append(title)
        return journal

    async def _issue(self, raw_data, journal: Journal) -> None:
        volume = raw_data.get("volume_s", None)
        numbers = raw_data.get("issue_s", [])
        source_identifier = (
            journal.source_identifier
            + f"-{volume}-{'-'.join(numbers)}"
            + f"-{self._get_source()}"
        )
        issue = await self._get_or_create_issue(
            IssueInformations(
                source=self._get_source(),
                source_identifier=source_identifier,
                journal=journal,
                volume=volume,
                number=numbers,
            )
        )
        if volume is not None and (volume != issue.volume):
            issue.volume = volume
        for number in numbers:
            if number not in issue.number:
                issue.number.append(number)
        return issue

    def _identifiers(self, raw_data):
        for field in self._keys_by_pattern(pattern=r".*Id_s", data=raw_data):
            if field in ("linkExtId_s", "europeanProjectCallId_s"):
                continue

            field_data = raw_data[field]
            if not isinstance(field_data, list):
                field_data = [field_data]

            identifier_type = self._identifier_type(field)
            if identifier_type is None:
                continue

            for value in field_data:
                if value in (None, ""):
                    continue
                yield ReferenceIdentifier(type=identifier_type, value=value)

    def _identifier_type(self, field: str) -> str | None:
        for pattern, identifier_type in self.FIELD_NAME_TO_IDENTIFIER_TYPE.items():
            if pattern in field:
                return identifier_type
        logger.error("Unknown identifier type from HAL for field %s", field)
        return None

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
                        code=code,
                        source=ConceptInformations.ConceptSources.JEL,
                    )
                )
            except AssertionError as error:
                logger.error(
                    f"Could not create JEL concept with code {code} because : {error}"
                )
                continue
        fields = self._keys_by_pattern(pattern=r".*_keyword_s", data=raw_data)
        for field in fields:
            for label in raw_data[field]:
                yield await self._get_or_create_concept_by_label(
                    ConceptInformations(
                        label=label, language=self._language_from_field_name(field)
                    )
                )

    async def _add_contributions(
        self, raw_data: dict, new_ref: Reference, tei_decoder: HalTEIDecoder = None
    ) -> None:
        # pylint: disable=too-many-locals
        number_of_contributors = len(
            raw_data.get("authFullNameFormIDPersonIDIDHal_fs", [])
        )
        if len(raw_data.get("authQuality_s", [])) != number_of_contributors:
            raise UnexpectedFormatException(
                "Number of qualities and contributors "
                f"is not the same for halId_s: {raw_data['halId_s']}"
            )
        contribution_informations = []
        first_names = raw_data.get("authFirstName_s", [])
        last_names = raw_data.get("authLastName_s", [])
        # if first_names or last_names length is not the same as the number of contributors
        # discard first names and last names, replace it with list of None of the same length
        if (
            len(first_names) != len(last_names)
            or len(first_names) != number_of_contributors
        ):
            first_names = [None] * number_of_contributors
            last_names = [None] * number_of_contributors
            logger.warning(
                "First names and last names are not the same length as "
                f"contributors for halId_s: {raw_data['halId_s']}"
            )
        for rank, contribution in enumerate(
            zip(
                raw_data.get("authQuality_s", []),
                raw_data.get("authFullNameFormIDPersonIDIDHal_fs", []),
                first_names,
                last_names,
            )
        ):
            quality, contributor, first_name, last_name = contribution
            if not re.match(r".*_FacetSep_.*-.*_FacetSep_", contributor):
                raise UnexpectedFormatException(
                    f"Unexpected format for contributor {contributor}"
                )
            name, ids, _ = contributor.split("_FacetSep_")
            form_id, id_hal = ids.split("-")
            contribution_informations.append(
                AbstractReferencesConverter.ContributionInformations(
                    role=HalRolesConverter.convert(quality),
                    identifier=id_hal if id_hal != "0" else form_id,
                    name=name,
                    first_name=first_name,
                    last_name=last_name,
                    rank=rank,
                    ext_identifiers=tei_decoder.get_identifiers(id_hal)
                    if tei_decoder
                    else [],
                )
            )
        async for contribution in self._contributions(
            contribution_informations=contribution_informations,
            source=self._get_source(),
        ):
            new_ref.contributions.append(contribution)

    def _organizations_from_contributor(
        self, raw_data, id_contributor
    ) -> Set[OrganizationInformations]:
        # Get the organizations informations of the contributor
        organizations = set()

        for auth_org in raw_data.get("authIdHasPrimaryStructure_fs", []):
            auth, org = auth_org.split("_JoinSep_")
            ids, _ = auth.split("_FacetSep_")
            _, id_hal = ids.split("-")
            if id_hal != id_contributor:
                continue

            org_id, org_name = org.split("_FacetSep_")
            organizations.add(
                OrganizationInformations(
                    name=org_name, identifier=org_id, source=self._get_source()
                )
            )
        return organizations

    async def _document_type(self, raw_data):
        uri, label = HalDocumentTypeConverter().convert(raw_data)
        return await self._get_or_create_document_type_by_uri(uri, label)

    def hash_keys(self, harvester_version: Version) -> list[HashKey]:
        return [
            HashKey("docid"),
            HashKey("citationRef_s"),
            HashKey("citationFull_s"),
            HashKey("en_title_s"),
            HashKey("en_keyword_s"),
            HashKey("en_abstract_s"),
            HashKey("authIdForm_i"),
            HashKey("authFullNameFormIDPersonIDIDHal_fs"),
            HashKey("authFirstName_s"),
            HashKey("authLastName_s"),
            HashKey("authIdHasPrimaryStructure_fs"),
            HashKey("labStructId_i"),
            HashKey("docType_s"),
            HashKey("publicationDate_tdate"),
            HashKey("publicationDate_s"),
            HashKey("producedDate_tdate"),
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

    def _add_hal_manifestation(self, raw_data, new_ref):
        uri = raw_data.get("uri_s", None)
        if uri is None:
            raise UnexpectedFormatException(
                f"uri_s is missing for halId_s: {raw_data['halId_s']}"
            )
        download_url = raw_data.get("fileMain_s", None)
        if download_url is None:
            download_url = raw_data.get("linkExtUrl_s", None)
        additional_files = raw_data.get("files_s", [])
        # keep only files after the first one
        additional_files = additional_files[1:]
        try:
            new_ref.manifestations.append(
                ReferenceManifestation(
                    page=uri,
                    download_url=download_url,
                    additional_files=additional_files,
                )
            )
        except ValueError as error:
            raise UnexpectedFormatException(
                f"Error while creating manifestation for halId_s: {raw_data['halId_s']}"
            ) from error
