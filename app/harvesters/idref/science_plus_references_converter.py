import rdflib
from rdflib import RDF, Literal, DCTERMS
from app.db.models.reference_identifier import ReferenceIdentifier
from app.db.models.reference import Reference

from app.db.models.title import Title
from app.harvesters.idref.abes_rdf_references_converter import (
    AbesRDFReferencesConverter,
)
from app.harvesters.idref.science_plus_document_type_converter import (
    SciencePlusDocumentTypeConverter,
)
from app.harvesters.rdf_harvester_raw_result import RdfHarvesterRawResult


class SciencePlusReferencesConverter(AbesRDFReferencesConverter):
    """
    Converts raw data from SciencePlus to a normalised Reference object
    """

    @AbesRDFReferencesConverter.validate_reference
    async def convert(self, raw_data: RdfHarvesterRawResult) -> Reference:
        new_ref = await super().convert(raw_data)

        if raw_data.doi:
            new_ref.identifiers.append(self._add_doi_identifier(raw_data.doi))
        new_ref.harvester = "idref.SciencePlus"
        return new_ref

    def _titles(self, pub_graph, uri):
        title: Literal
        for title in pub_graph.objects(rdflib.term.URIRef(uri), DCTERMS.title):
            yield Title(value=title.value, language=title.language)

    def _add_doi_identifier(self, doi: str):
        return ReferenceIdentifier(value=doi, type="doi")

    async def _document_type(self, pub_graph, uri):
        cache = {}
        document_type: Literal
        for document_type in pub_graph.objects(rdflib.term.URIRef(uri), RDF.type):
            if document_type in cache:
                yield cache[document_type]
                continue
            uri, label = SciencePlusDocumentTypeConverter().convert(str(document_type))
            document_type_db = await self._get_or_create_document_type_by_uri(
                uri, label
            )
            cache[document_type] = document_type_db
            yield document_type_db
