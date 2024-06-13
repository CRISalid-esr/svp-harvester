import re
from typing import Generator, List

from loguru import logger
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
from app.harvesters.hal.hal_document_type_converter import HalDocumentTypeConverter
from app.harvesters.hal.hal_roles_converter import HalRolesConverter
from app.harvesters.json_harvester_raw_result import (
    JsonHarvesterRawResult as JsonRawResult,
)
from app.services.book.book_data_class import BookInformations
from app.services.concepts.concept_informations import ConceptInformations
from app.services.hash.hash_key import HashKey
from app.services.issue.issue_data_class import IssueInformations
from app.services.journal.journal_data_class import JournalInformations
from app.services.organizations.organization_data_class import OrganizationInformations
from app.utilities.date_utilities import check_valid_iso8601_date
from app.utilities.isbn_utilities import get_isbns
from app.utilities.string_utilities import normalize_string


class HalReferencesConverter(AbstractReferencesConverter):
    """
    Converts raw data from HAL to a normalised Reference object
    """

    FIElD_NAME_TO_IDENTIFIER_TYPE: dict[str, str] = {
        "arxivId_s": "arxiv",
        "bibcodeId_s": "bibcode",
        "biorxivId_s": "biorxiv",
        "cernId_s": "cern",
        "chemrxivId_s": "chemrxiv",
        "doiId_s": "doi",
        "ensamId_s": "ensam",
        "halId_s": "hal",
        "inerisId_s": "ineris",
        "inspireId_s": "inspire",
        "irdId_s": "ird",
        "irsteaId_s": "irstea",
        "irThesaurusId_s": "ir_thesaurus",
        "meditagriId_s": "meditagri",
        "nntId_s": "nnt",
        "okinaId_s": "okina",
        "oataoId_s": "oatao",
        "piiId_s": "pii",
        "ppnId_s": "ppn",
        "prodinraId_s": "prodinra",
        "pubmedId_s": "pubmed",
        "pubmedcentralId_s": "pubmedcentral",
        "sciencespoId_s": "sciencespo",
        "swhidId_s": "swhid",
        "wosId_s": "wos",
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
        await self._add_contributions(json_payload, new_ref)

        await self._add_hal_manifestation(json_payload, new_ref)

        self._add_issued_date(json_payload, new_ref)

        self._add_created_date(json_payload, new_ref)

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
            new_ref.issued = check_valid_iso8601_date(
                json_payload.get("publicationDate_tdate", None)
            )
        except UnexpectedFormatException as error:
            logger.error(
                f"Hal reference converter cannot create issued date from publicationDate_tdate in"
                f" {json_payload['halId_s']}: {error}"
            )

    def _harvester(self) -> str:
        return "HAL"

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
                source="hal",
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
                source=self._harvester(),
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
            normalize_string("-".join(journal.titles))
            + f"-{volume}-{'-'.join(numbers)}"
            + f"-{self._harvester()}"
        )
        issue = await self._get_or_create_issue(
            IssueInformations(
                source=self._harvester(),
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
            for value in field_data:
                identifier_type = self._identifier_type(field)
                if identifier_type is not None:
                    yield ReferenceIdentifier(type=identifier_type, value=value)

    def _identifier_type(self, field):
        for pattern, identifier_type in self.FIElD_NAME_TO_IDENTIFIER_TYPE.items():
            if pattern in field:
                return identifier_type
        logger.error(f"Unknown identifier type from Hal for field {field}")
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
                    role=HalRolesConverter.convert(quality),
                    identifier=id_hal if id_hal != "0" else None,
                    name=name,
                    rank=rank,
                )
            )
        async for contribution in self._contributions(
            contribution_informations=contribution_informations, source="hal"
        ):
            new_ref.contributions.append(contribution)

    async def _add_organization(self, raw_data: dict, new_ref: Reference) -> None:
        # For each contribution, get the organizations of the contributor
        # and add them to the contribution
        for contribution in new_ref.contributions:
            organizations = self._organizations_from_contributor(
                raw_data, contribution.contributor.source_identifier
            )
            async for org in self._organizations(organizations):
                contribution.affiliations.append(org)

    def _organizations_from_contributor(
        self, raw_data, id_contributor
    ) -> List[OrganizationInformations]:
        # Get the organizations informations of the contributor
        organizations = set()

        for auth_org in raw_data.get("authIdHasStructure_fs", []):
            auth, org = auth_org.split("_JoinSep_")
            ids, _ = auth.split("_FacetSep_")
            _, id_hal = ids.split("-")
            if id_hal != id_contributor:
                continue

            org_id, org_name = org.split("_FacetSep_")
            organizations.add(
                OrganizationInformations(name=org_name, identifier=org_id, source="hal")
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
            HashKey("authIdHasStructure_fs"),
            HashKey("labStructId_i"),
            HashKey("docType_s"),
            HashKey("publicationDate_tdate"),
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

    # What we receive :
    # [
    #       {
    #         "_comment": "Basic use case with uri_s only and no files",
    #         "docid": "3068",
    #         "citationRef_s": "<i>Physical Review E : Statistical, Nonlinear, and Soft Matter Physics</i>, 2003, 67, pp.051910",
    #         "citationFull_s": "A. Crut, D. Lasne, Jean-François Allemand, M. Dahan, P. Desbiolles. Transverse fluctuations of single DNA molecules attached to a surface by their extremities. <i>Physical Review E : Statistical, Nonlinear, and Soft Matter Physics</i>, 2003, 67, pp.051910. <a target=\"_blank\" href=\"https://hal.science/hal-00002447\">&#x27E8;hal-00002447&#x27E9;</a>",
    #         "en_title_s": [
    #           "Transverse fluctuations of single DNA molecules attached to a surface by their extremities"
    #         ],
    #         "journalId_i": 21487,
    #         "journalTitle_s": "Physical Review E : Statistical, Nonlinear, and Soft Matter Physics",
    #         "journalPublisher_s": "American Physical Society",
    #         "journalIssn_s": "1539-3755",
    #         "journalEissn_s": "1550-2376",
    #         "halId_s": "hal-00002447",
    #         "uri_s": "https://hal.science/hal-00002447",
    #         "docType_s": "ART",
    #         "page_s": "051910",
    #         "volume_s": "67",
    #         "producedDate_tdate": "2003-01-01T00:00:00Z",
    #         "publicationDate_tdate": "2003-01-01T00:00:00Z"
    #       },
    #       {
    #         "_comment": "Basic use case with uri_s and a single file",
    #         "docid": "440439",
    #         "citationRef_s": "<i>Physical Review B: Condensed Matter and Materials Physics (1998-2015)</i>, 2009, 80 (19), pp.195406. <a target=\"_blank\" href=\"https://dx.doi.org/10.1103/PhysRevB.80.195406\">&#x27E8;10.1103/PhysRevB.80.195406&#x27E9;</a>",
    #         "citationFull_s": "Vincent Juvé, Mattia Scardamaglia, Paolo Maioli, Aurélien Crut, Samy Merabia, et al.. Cooling dynamics and thermal interface resistance of glass-embedded metal nanoparticles. <i>Physical Review B: Condensed Matter and Materials Physics (1998-2015)</i>, 2009, 80 (19), pp.195406. <a target=\"_blank\" href=\"https://dx.doi.org/10.1103/PhysRevB.80.195406\">&#x27E8;10.1103/PhysRevB.80.195406&#x27E9;</a>. <a target=\"_blank\" href=\"https://hal.science/hal-00440439\">&#x27E8;hal-00440439&#x27E9;</a>",
    #         "linkExtUrl_s": "http://arxiv.org/pdf/0912.3058",
    #         "linkExtId_s": "arxiv",
    #         "en_title_s": [
    #           "Cooling dynamics and thermal interface resistance of glass-embedded metal nanoparticles"
    #         ],
    #         "journalId_i": 17977,
    #         "journalTitle_s": "Physical Review B: Condensed Matter and Materials Physics (1998-2015)",
    #         "journalPublisher_s": "American Physical Society",
    #         "journalIssn_s": "1098-0121",
    #         "journalEissn_s": "1550-235X",
    #         "halId_s": "hal-00440439",
    #         "uri_s": "https://hal.science/hal-00440439",
    #         "docType_s": "ART",
    #         "issue_s": [
    #           "19"
    #         ],
    #         "page_s": "195406",
    #         "volume_s": "80",
    #         "doiId_s": "10.1103/PhysRevB.80.195406",
    #         "arxivId_s": "0912.3058",
    #         "producedDate_tdate": "2009-11-05T00:00:00Z",
    #         "publicationDate_tdate": "2009-11-05T00:00:00Z",
    #         "fileMain_s": "https://hal.science/hal-00440439/document",
    #         "files_s": [
    #           "https://hal.science/hal-00440439/file/Juve_et_al._PRB_2009.pdf"
    #         ]
    #       },
    #       {
    #         "_comment": "Basic use case with uri_s and multiple files",
    #         "docid": "1714043",
    #         "citationRef_s": "<i>Journal of Physical Chemistry C</i>, 2015, 119 (3), pp.1591-1599. <a target=\"_blank\" href=\"https://dx.doi.org/10.1021/jp511070h\">&#x27E8;10.1021/jp511070h&#x27E9;</a>",
    #         "citationFull_s": "Tatjana Stoll, Paolo Maioli, Aurélien Crut, Julien Burgin, Pierre Langot, et al.. Ultrafast Acoustic Vibrations of Bimetallic Nanoparticles. <i>Journal of Physical Chemistry C</i>, 2015, 119 (3), pp.1591-1599. <a target=\"_blank\" href=\"https://dx.doi.org/10.1021/jp511070h\">&#x27E8;10.1021/jp511070h&#x27E9;</a>. <a target=\"_blank\" href=\"https://hal.science/hal-01115164\">&#x27E8;hal-01115164&#x27E9;</a>",
    #         "linkExtUrl_s": "https://hal.archives-ouvertes.fr/hal-01115164/file/StollJPC-c2015_Postprint.pdf",
    #         "linkExtId_s": "openaccess",
    #         "en_title_s": [
    #           "Ultrafast Acoustic Vibrations of Bimetallic Nanoparticles"
    #         ],
    #         "en_abstract_s": [
    #           "Investigations of the ultrafast acoustic response of metal nanosystems yield important information on the validity of continuous elastic mechanics at the nanoscale and also provide an optical way to probe nanoobject morphologies. In this context, we used femtosecond time-resolved pump-probe spectroscopy to study two classes of bimetallic nanoparticles: chemically synthesized AuAg nanospheres in water in the 20-45 nm size range, both with alloyed and segregated core-shell morphologies, and mass-selected glass-embedded PtAu core-shell nanospheres in the very small size range (2.3-2.5 nm), synthesized by physical methods. The analysis of the corresponding breathing mode periods demonstrates validity of the predictions of the continuous elastic model for bimetallic nanoobjects with the investigated sizes, morphologies and composition. Moreover, discrimination of nanoparticles internal structure (alloy or core-shell) by measurement of their acoustic response is also demonstrated."
    #         ],
    #         "journalId_i": 16014,
    #         "journalTitle_s": "Journal of Physical Chemistry C",
    #         "journalPublisher_s": "American Chemical Society",
    #         "journalIssn_s": "1932-7447",
    #         "journalEissn_s": "1932-7455",
    #         "halId_s": "hal-01115164",
    #         "uri_s": "https://hal.science/hal-01115164",
    #         "docType_s": "ART",
    #         "issue_s": [
    #           "3"
    #         ],
    #         "page_s": "1591-1599",
    #         "volume_s": "119",
    #         "doiId_s": "10.1021/jp511070h",
    #         "producedDate_tdate": "2015-01-01T00:00:00Z",
    #         "publicationDate_tdate": "2015-01-01T00:00:00Z",
    #         "fileMain_s": "https://hal.science/hal-01115164/document",
    #         "files_s": [
    #           "https://hal.science/hal-01115164/file/StollJPC-c2015_Postprint.pdf",
    #           "https://hal.science/hal-01115164/file/annexe.pdf"
    #         ]
    #       },
    #       {
    #         "_comment": "Use case with uri_s file only available from external source linkExtUrl_s",
    #         "docid": "3118741",
    #         "citationRef_s": "<i>Advanced Optical Materials</i>, 2016, 4 (4), pp.567-577. <a target=\"_blank\" href=\"https://dx.doi.org/10.1002/adom.201500548\">&#x27E8;10.1002/adom.201500548&#x27E9;</a>",
    #         "citationFull_s": "Etienne Pertreux, Anna Lombardi, Ileana Florea, Miguel Spuch-Calvar, Sergio Gómez-Graña, et al.. Surface plasmon resonance of an individual nano-object on an absorbing substrate : quantitative effects of distance and 3D orientation. <i>Advanced Optical Materials</i>, 2016, 4 (4), pp.567-577. <a target=\"_blank\" href=\"https://dx.doi.org/10.1002/adom.201500548\">&#x27E8;10.1002/adom.201500548&#x27E9;</a>. <a target=\"_blank\" href=\"https://hal.science/hal-01309285\">&#x27E8;hal-01309285&#x27E9;</a>",
    #         "linkExtUrl_s": "https://api.istex.fr/ark:/67375/WNG-WBH7WTX8-W/fulltext.pdf?sid=hal",
    #         "linkExtId_s": "istex",
    #         "en_title_s": [
    #           "Surface plasmon resonance of an individual nano-object on an absorbing substrate : quantitative effects of distance and 3D orientation"
    #         ],
    #         "en_abstract_s": [
    #           "Modification of the plasmonic response of a metal nano-object due to interaction with a substrate is experimentally investigated measuring the quantitative optical extinction spectra of individual nano-objects with various elongated shapes (bipyramids and rods) deposited on a dielectric (silica) or absorbing (carbon) membrane. Apart from the expected dependence of the nanoparticle surface plasmon resonance (SPR) frequency on the nature of the substrate, large substrate and particle shape dependent modifications of its SPR width are demonstrated. These dependencies are ascribed to strong localization of the electromagnetic field associated with the longitudinal SPR of an elongated nano-object around its tips, leading to different interaction with the substrate depending on the particle shape and 3D orientation relative to the substrate. Both parameters have been precisely determined by electron tomography, permitting excellent reproduction of the experimental data. Experiments performed on silver-encapsulated bipyramids, whose shape evolves from a pyramidal one towards a cylindrical one, further confirm this effect."
    #         ],
    #         "halId_s": "hal-01309285",
    #         "uri_s": "https://hal.science/hal-01309285",
    #         "docType_s": "ART",
    #         "producedDate_tdate": "2016-01-01T00:00:00Z",
    #         "publicationDate_tdate": "2016-01-01T00:00:00Z"
    #       }
    #     ]
    #
    #
    # @pytest.mark.current
    # async def test_publication_without_files(hal_api_docs_for_researcher_with_uris: dict):
    #     """
    #     Given a list of docs where the first is a publication without files
    #     When the converter is called with the first doc
    #     Then it should return a reference with a single manifestion whith uri_s as page field
    #
    #
    #     :param hal_api_docs_for_researcher_with_uris:
    #     :return:
    #     """
    #     converter_under_tests = HalReferencesConverter()
    #     doc = hal_api_docs_for_researcher_with_uris["response"]["docs"][0]
    #     result = JsonHarvesterRawResult(
    #         source_identifier=doc["docid"], payload=doc, formatter_name="HAL"
    #     )
    #     reference = converter_under_tests.build(
    #         raw_data=result, harvester_version=VersionInfo.parse("0.0.0")
    #     )
    #     await converter_under_tests.convert(raw_data=result, new_ref=reference)
    #     assert len(reference.manifestations) == 1
    #     assert reference.manifestations[0].page == doc["uri_s"]
    #
    #
    # @pytest.mark.current
    # async def test_publication_with_file(hal_api_docs_for_researcher_with_uris: dict):
    #     """
    #     Given a list of docs where the second is a publication with a sigle file in fileMain_s
    #     When the converter is called with the second doc
    #     Then it should return a reference with a single manifestion whith uri_s as page field
    #     and the fileMain_s as download_url field
    #
    #     :param hal_api_docs_for_researcher_with_uris:
    #     :return:
    #     """
    #     converter_under_tests = HalReferencesConverter()
    #     doc = hal_api_docs_for_researcher_with_uris["response"]["docs"][1]
    #     result = JsonHarvesterRawResult(
    #         source_identifier=doc["docid"], payload=doc, formatter_name="HAL"
    #     )
    #     reference = converter_under_tests.build(
    #         raw_data=result, harvester_version=VersionInfo.parse("0.0.0")
    #     )
    #     await converter_under_tests.convert(raw_data=result, new_ref=reference)
    #     assert len(reference.manifestations) == 1
    #     assert reference.manifestations[0].page == doc["uri_s"]
    #     assert reference.manifestations[0].download_url == doc["fileMain_s"]
    #
    #
    # @pytest.mark.current
    # async def test_publication_with_files(hal_api_docs_for_researcher_with_uris: dict):
    #     """
    #     Given a list of docs where the third is a publication with multiple files in files_s
    #     When the converter is called with the third doc
    #     Then it should return a reference with a single manifestion whith uri_s as page field
    #     and the fileMain_s as download_url field
    #     and the files after the first one from files_s as additional_files
    #
    #     :param hal_api_docs_for_researcher_with_uris:
    #     :return:
    #     """
    #     converter_under_tests = HalReferencesConverter()
    #     doc = hal_api_docs_for_researcher_with_uris["response"]["docs"][2]
    #     result = JsonHarvesterRawResult(
    #         source_identifier=doc["docid"], payload=doc, formatter_name="HAL"
    #     )
    #     reference = converter_under_tests.build(
    #         raw_data=result, harvester_version=VersionInfo.parse("0.0.0")
    #     )
    #     await converter_under_tests.convert(raw_data=result, new_ref=reference)
    #     assert len(reference.manifestations) == 1
    #     assert reference.manifestations[0].page == doc["uri_s"]
    #     assert reference.manifestations[0].download_url == doc["fileMain_s"]
    #     assert len(reference.manifestations[0].additional_files) == 1
    #     assert reference.manifestations[0].additional_files[0] == doc["files_s"][1]
    def _add_hal_manifestation(self, raw_data, new_ref):
        # add a manifestation to the reference
        # take uri_s as page or raise an error if not present
        # take fileMain_s as download_url or linkExtUrl_s if not present
        # or None if neither is present
        # if fileMain_s is present, take all files_s as additional_files but ignore the first one

        uri = raw_data.get("uri_s", None)
        if uri is None:
            raise UnexpectedFormatException(
                f"uri_s is missing for halId_s: {raw_data['halId_s']}"
            )
        download_url = raw_data.get("fileMain_s", None)
        if download_url is None:
            download_url = raw_data.get("linkExtUrl_s", None)
        additional_files = raw_data.get("files_s", [])
        if download_url is None and len(additional_files) > 0:
            download_url = additional_files.pop(0)
        # a ValueError could be raised if one of the URI is not a valid URI
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
