from xml.etree.ElementTree import Element
import isodate
from loguru import logger
from app.db.models.abstract import Abstract
from app.db.models.issue import Issue
from app.db.models.journal import Journal
from app.db.models.reference import Reference
from app.db.models.reference_identifier import ReferenceIdentifier
from app.db.models.title import Title
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.scopus.scopus_client import ScopusClient
from app.harvesters.scopus.scopus_document_type_converter import (
    ScopusDocumentTypeConverter,
)
from app.harvesters.xml_harvester_raw_result import XMLHarvesterRawResult
from app.db.models.contribution import Contribution
from app.services.concepts.concept_informations import ConceptInformations
from app.services.hash.hash_key_xml import HashKeyXML
from app.services.issue.issue_data_class import IssueInformations
from app.services.journal.journal_data_class import JournalInformations
from app.services.organizations.organization_data_class import OrganizationInformations
from app.utilities.string_utilities import normalize_string


class ScopusReferencesConverter(AbstractReferencesConverter):
    """
    Converts raw data from Scopus API to a normalised Reference Object
    """

    FIELD_NAME_IDENTIFIER = {
        "prism:doi": "doi",
        "default:pubmed-id": "pubmed",
    }

    @AbstractReferencesConverter.validate_reference
    async def convert(
        self, raw_data: XMLHarvesterRawResult, new_ref: Reference
    ) -> None:
        entry: Element = raw_data.payload

        async for title in self._title(entry):
            new_ref.titles.append(title)

        abstract = self._abstract(entry)
        async for abstract in self._abstract(entry):
            new_ref.abstracts.append(abstract)

        async for document_type in self._document_type(entry):
            new_ref.document_type.append(document_type)

        async for identifier in self._indetifiers(entry):
            new_ref.identifiers.append(identifier)

        async for concept in self._concepts(entry):
            new_ref.subjects.append(concept)

        async for contribution in self._add_contributions(entry):
            new_ref.contributions.append(contribution)

        issued = self._issued(entry)
        if issued is not None:
            new_ref.issued = issued

        journal = await self._journal(entry)
        if journal is not None:
            issue = await self._issue(entry, journal)
            new_ref.issue = issue

        new_ref.page = (
            self._get_element(entry, "prism:pageRange").text
            if self._get_element(entry, "prism:pageRange") is not None
            else None
        )

    async def _journal(self, entry: Element) -> Journal | None:
        issn = self._get_element(entry, "prism:issn")
        eissn = self._get_element(entry, "prism:eIssn")
        title = self._get_element(entry, "prism:publicationName")
        source_identifier = self._get_element(entry, "default:source-id")
        if (issn is None and eissn is None) or (source_identifier is None):
            return None

        journal = await self._get_or_create_journal(
            JournalInformations(
                issn=[f"{issn.text[:4]}-{issn.text[4:]}"] if issn is not None else None,
                eissn=(
                    [f"{eissn.text[:4]}-{eissn.text[4:]}"]
                    if eissn is not None
                    else None
                ),
                titles=[title.text] if title is not None else [],
                source=self._harvester(),
                source_identifier=source_identifier.text,
            )
        )
        return journal

    async def _issue(self, entry: Element, journal: Journal) -> Issue:
        volume = self._get_element(entry, "prism:volume")
        number = self._get_element(entry, "prism:issueIdentifier")
        source_identifier = (
            normalize_string("-".join(journal.titles))
            + f"-{volume.text if volume is not None else ''}-"
            + f"{number.text if number is not None else ''}-"
            + f"{self._harvester()}"
        )
        issue = await self._get_or_create_issue(
            IssueInformations(
                source=self._harvester(),
                journal=journal,
                volume=volume.text if volume is not None else None,
                number=[number.text] if number is not None else [],
                source_identifier=source_identifier,
            )
        )
        return issue

    async def _concepts(self, entry: Element):
        concepts = self._get_element(entry, "default:authkeywords")
        if concepts is not None:
            for concept in concepts.text.split(" | "):
                concept_db = await self._get_or_create_concept_by_label(
                    ConceptInformations(label=concept)
                )
                yield concept_db

    def _get_affiliation(self, entry: Element):
        """
        Return a dict as {afid: OrganizationInformations}
        """
        affiliations = self._get_elements(entry, "default:affiliation")
        dict_affiliations = {}
        for affiliation in affiliations:
            afid = self._get_element(affiliation, "default:afid").text
            name = self._get_element(affiliation, "default:affilname").text
            afiliation_information = OrganizationInformations(
                name=name, identifier=afid, source="scopus"
            )
            dict_affiliations[afid] = afiliation_information
        return dict_affiliations

    async def _add_contributions(self, entry: Element):
        contributor_affiliation = {}
        authors = self._get_elements(entry, "default:author")
        contributions = []
        for author in authors:
            afiliations = self._get_elements(author, "default:afid")
            rank = author.attrib["seq"]
            identifier = self._get_element(author, "default:authid").text
            name = self._get_element(author, "default:authname").text
            contributions.append(
                AbstractReferencesConverter.ContributionInformations(
                    role=Contribution.Role.AUTHOR.value,
                    identifier=identifier,
                    name=name,
                    rank=int(rank),
                )
            )
            contributor_affiliation[identifier] = [
                afiliation.text for afiliation in afiliations
            ]

        affiliations = self._get_affiliation(entry)

        async for contribution in self._contributions(
            contribution_informations=contributions, source="scopus"
        ):
            list_affiliations = []
            for id_affiliation in contributor_affiliation[
                contribution.contributor.source_identifier
            ]:
                affiliation = affiliations.get(id_affiliation, None)
                if affiliation is not None:
                    list_affiliations.append(affiliation)
            async for org in self._organizations(list_affiliations):
                contribution.affiliations.append(org)
            yield contribution

    async def _abstract(self, entry: Element):
        for abstract in self._get_elements(entry, "dc:description"):
            yield Abstract(value=abstract.text) if abstract is not None else None

    async def _document_type(self, entry: Element):
        for document_type in self._get_elements(entry, "default:subtype"):
            uri, label = ScopusDocumentTypeConverter().convert(document_type.text)
            yield await self._get_or_create_document_type_by_uri(uri=uri, label=label)

    async def _indetifiers(self, entry: Element):
        for key_identifier, type_identifier in self.FIELD_NAME_IDENTIFIER.items():
            identifier = self._get_element(entry, key_identifier)
            if identifier is not None:
                yield ReferenceIdentifier(
                    type=type_identifier,
                    value=identifier.text,
                )

    async def _title(self, entry: Element):
        for title in self._get_elements(entry, "dc:title"):
            yield Title(value=title.text)

    def _issued(self, entry: Element):
        issued = self._get_element(entry, "prism:coverDate")
        return self._date(issued.text)

    def _get_element(self, entry: Element, tag: str) -> Element | None:
        return entry.find(tag, ScopusClient.NAMESPACE)

    def _get_elements(self, entry: Element, tag: str) -> list[Element]:
        return entry.findall(tag, ScopusClient.NAMESPACE)

    def _date(self, date):
        try:
            if date is None:
                return None
            return isodate.parse_date(date)
        except isodate.ISO8601Error as error:
            logger.error(f"Could not parse date {date} from Scopus with error {error}")
            return None

    def _harvester(self) -> str:
        return "Scopus"

    def hash_keys(self) -> list[str]:
        return [
            HashKeyXML("prism:url", namespace=ScopusClient.NAMESPACE),
            HashKeyXML("dc:identifier", namespace=ScopusClient.NAMESPACE),
            HashKeyXML("dc:title", namespace=ScopusClient.NAMESPACE),
            HashKeyXML("dc:description", namespace=ScopusClient.NAMESPACE),
            HashKeyXML("default:subtype", namespace=ScopusClient.NAMESPACE),
            HashKeyXML("prism:coverDate", namespace=ScopusClient.NAMESPACE),
            HashKeyXML("prism:doi", namespace=ScopusClient.NAMESPACE),
            HashKeyXML("prism:issn", namespace=ScopusClient.NAMESPACE),
            HashKeyXML("default:authkeywords", namespace=ScopusClient.NAMESPACE),
            HashKeyXML("default:affiliation", namespace=ScopusClient.NAMESPACE),
            HashKeyXML(
                "default:author", namespace=ScopusClient.NAMESPACE, sorted=False
            ),
        ]
