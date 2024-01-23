from xml.etree import ElementTree

from app.db.models.abstract import Abstract
from app.db.models.reference import Reference
from app.db.models.title import Title
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.rdf_harvester_raw_result import (
    RdfHarvesterRawResult as RdfRawResult,
)


class OpenEditionReferencesConverter(AbstractReferencesConverter):
    """
    Convert the publication from the OpenEdition to a normalised Reference object
    """

    BASE_DOMAIN = "{http://www.openarchives.org/OAI/2.0/}"
    NAMESPACE = "{http://www.bl.uk/namespaces/oai_dcq/}"
    W3_NAMESPACE = "{http://www.w3.org/XML/1998/namespace}"
    TERMS = "{http://purl.org/dc/terms/}"

    async def convert(self, raw_data: RdfRawResult) -> Reference:
        new_ref: Reference = Reference()

        new_ref.source_identifier = raw_data.source_identifier

        root: ElementTree = self._get_root_data(raw_data.payload)
        new_ref.titles.append(self._title(root))

        for abstract in self._abstracts(root):
            new_ref.abstracts.append(abstract)

        async for subject in self._subjects(root):
            if subject.id is None or subject.id not in list(
                map(lambda s: s.id, new_ref.subjects)
            ):
                new_ref.subjects.append(subject)

        # TODO : handle document type, where get URI ?
        # new_ref.document_type.append(await self._document_type(root))

        # TODO handle contributor

        # TODO where get subtitle ?

        new_ref.hash = self._hash(self._create_dict(root))
        return new_ref

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

    def _get_root_data(self, root):
        return (
            root.find(f"{self.BASE_DOMAIN}GetRecord")
            .find(f"{self.BASE_DOMAIN}record")
            .find(f"{self.BASE_DOMAIN}metadata")
            .find(f"{self.NAMESPACE}qualifieddc")
        )

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
        if len(abstract) == 0:
            yield Abstract(value=None, language=None)
        for value, attrib in abstract:
            # check if language defined, If not then we take the language of the document
            try:
                language = attrib[f"{self.W3_NAMESPACE}lang"]
            except KeyError:
                language = self._language(root)
            yield Abstract(value=value, language=language)

    async def _subjects(self, root: ElementTree):
        # TODO : handle subject WITH URI ?
        subjects = self._get_terms(root, "subject")
        language = self._language(root)
        for subject in subjects:
            value, attrib = subject
            language = attrib[f"{self.W3_NAMESPACE}lang"]
            yield await self._get_or_create_concept_by_label(
                value=value, language=language
            )

    # TODO: Handle type document, in xml we have for example <dcterms:type>article</dcterms:type>.
    # Where Get URI ?
    # async def _document_type(self, root: ElementTree):
    #     document_type = self._get_term(root, "type")
    #     language = self._get_language(root)
    #     return await self._get_or_create_document_type_by_uri(
    #         value=document_type, language=language
    #     )

    def _hash_keys(self) -> list[str]:
        return ["title", "abstract", "type", "language", "identifier", "subject"]

    def _create_dict(self, root: ElementTree):
        new_dict = {}
        for term in self._hash_keys():
            new_dict[term] = self._get_terms(root, term)

        return new_dict
