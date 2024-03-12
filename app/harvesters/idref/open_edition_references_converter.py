from typing import Generator
from xml.etree import ElementTree

from loguru import logger

from app.db.models.abstract import Abstract
from app.db.models.reference import Reference
from app.db.models.reference_identifier import ReferenceIdentifier
from app.db.models.title import Title
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.exceptions.unexpected_format_exception import (
    UnexpectedFormatException,
)
from app.harvesters.idref.open_edition_document_type_converter import (
    OpenEditionDocumentTypeConverter,
)
from app.harvesters.idref.open_edition_qualities_converter import (
    OpenEditionQualitiesConverter,
)
from app.harvesters.xml_harvester_raw_result import XMLHarvesterRawResult
from app.services.concepts.concept_informations import ConceptInformations
from app.services.hash.hash_key import HashKey


class OpenEditionReferencesConverter(AbstractReferencesConverter):
    """
    Convert the publication from the OpenEdition to a normalised Reference object
    """

    BASE_DOMAIN = "{http://www.openarchives.org/OAI/2.0/}"
    NAMESPACE = "{http://www.bl.uk/namespaces/oai_dcq/}"
    W3_NAMESPACE = "{http://www.w3.org/XML/1998/namespace}"
    TERMS = "{http://purl.org/dc/terms/}"

    def __init__(self):
        self.tree_root: ElementTree = None

    def _harvester(self) -> str:
        return "Idref"

    @AbstractReferencesConverter.validate_reference
    async def convert(
        self, raw_data: XMLHarvesterRawResult, new_ref: Reference
    ) -> None:
        new_ref.titles.append(self._title(self._get_root(raw_data)))

        for abstract in self._abstracts(self._get_root(raw_data)):
            new_ref.abstracts.append(abstract)

        async for subject in self._subjects(self._get_root(raw_data)):
            if subject.id is None or subject.id not in list(
                map(lambda s: s.id, new_ref.subjects)
            ):
                new_ref.subjects.append(subject)

        for identifier in self._reference_identifier(self._get_root(raw_data)):
            new_ref.identifiers.append(identifier)

        new_ref.document_type.append(
            await self._document_type(self._get_root(raw_data))
        )

        await self._add_contributions(new_ref, self._get_root(raw_data))

    def hash(self, raw_data: XMLHarvesterRawResult):
        return self._hash_dict(self._create_dict(self._get_root(raw_data)))

    def _reference_identifier(
        self, root: ElementTree
    ) -> Generator[ReferenceIdentifier, None, None]:
        for identifier in self._get_terms(root, "identifier"):
            if identifier[1]["scheme"] == "URI":
                yield ReferenceIdentifier(
                    value=identifier[0],
                    type="uri",
                )
            elif identifier[1]["scheme"] == "URN" and "urn:doi:" in identifier[0]:
                yield ReferenceIdentifier(
                    value=identifier[0].replace("urn:doi:", ""),
                    type="doi",
                )

    async def _add_contributions(self, new_ref: Reference, root: ElementTree) -> None:
        contribution_informations = []
        for open_edition_quality, contributors in [
            (open_edition_role, self._get_terms(root, open_edition_role))
            for open_edition_role in OpenEditionQualitiesConverter.ROLES_MAPPING
        ]:
            if len(contributors) == 0:
                continue
            for contributor_name, _ in contributors:
                contribution_informations.append(
                    AbstractReferencesConverter.ContributionInformations(
                        role=OpenEditionQualitiesConverter.convert(
                            open_edition_quality
                        ),
                        identifier=None,
                        name=contributor_name,
                        rank=None,
                    )
                )
        async for contribution in self._contributions(
            contribution_informations=contribution_informations, source="openedition"
        ):
            new_ref.contributions.append(contribution)

    def _get_term(self, root: ElementTree, term: str):
        return (
            root.find(f"{self.TERMS}{term}").text
            if root.find(f"{self.TERMS}{term}") is not None
            else None
        )

    def _get_terms(self, root: ElementTree, term: str):
        return [
            (term.text, term.attrib) for term in root.findall(f"{self.TERMS}{term}")
        ]

    def _get_root(self, raw_data: XMLHarvesterRawResult):
        if self.tree_root is None:
            try:
                root = raw_data.payload
                return (
                    root.find(f"{self.BASE_DOMAIN}GetRecord")
                    .find(f"{self.BASE_DOMAIN}record")
                    .find(f"{self.BASE_DOMAIN}metadata")
                    .find(f"{self.NAMESPACE}qualifieddc")
                )
            except AttributeError as error:
                raise UnexpectedFormatException(
                    "Unexpected format for OAI Open Edition response "
                    f"for {raw_data.source_identifier}"
                ) from error
        return self.tree_root

    def _title(self, root: ElementTree):
        title = self._get_term(root, "title")
        language = self._language(root)
        return Title(value=title, language=language)

    def _language(self, root: ElementTree):
        return self._get_term(root, "language")

    def _abstracts(self, root: ElementTree):
        # Sometimes we have abstract or description.
        # Is the same ? In Dublic Core, Abstract is a sub property of Description
        abstract = self._get_terms(root, "abstract")
        if len(abstract) == 0:
            abstract = self._get_terms(root, "description")
            if len(abstract) != 0:
                logger.debug("Description found instead of abstract")
        if len(abstract) == 0:
            yield
        for value, attrib in abstract:
            # check if language defined, If not then we take the language of the document
            try:
                language = attrib[f"{self.W3_NAMESPACE}lang"]
            except KeyError:
                language = self._language(root)
            yield Abstract(value=value, language=language)

    async def _subjects(self, root: ElementTree):
        subjects = self._get_terms(root, "subject")
        language = self._language(root)
        for subject in subjects:
            label, attrib = subject
            try:
                language = attrib[f"{self.W3_NAMESPACE}lang"]
            except KeyError:
                language = None
            yield await self._get_or_create_concept_by_label(
                ConceptInformations(
                    label=label,
                    language=language,
                )
            )

    async def _document_type(self, root: ElementTree):
        document_type = self._get_term(root, "type")
        uri, label = OpenEditionDocumentTypeConverter.convert(document_type)
        return await self._get_or_create_document_type_by_uri(uri=uri, label=label)

    def hash_keys(self) -> list[str]:
        return [
            HashKey("dcterms:title"),
            HashKey("dcterms:abstract"),
            HashKey("dcterms:type"),
            HashKey("dcterms:language"),
            HashKey("dcterms:identifier"),
            HashKey("dcterms:subject"),
            HashKey("dcterms:type"),
        ]

    def _create_dict(self, root: ElementTree):
        new_dict = {}
        for term in self.hash_keys():
            new_dict[term] = self._get_terms(root, term)

        return new_dict
