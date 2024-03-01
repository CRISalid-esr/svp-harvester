import rdflib
from rdflib import DC, Literal

from app.db.models.title import Title
from app.harvesters.idref.abes_rdf_references_converter import (
    AbesRDFReferencesConverter,
)
from app.harvesters.idref.sudoc_document_type_converter import (
    SudocDocumentTypeConverter,
)
from app.utilities.string_utilities import remove_after_separator


class SudocReferencesConverter(AbesRDFReferencesConverter):
    """
    Converts raw data from Sudoc to a normalised Reference object
    """

    def _harvester(self) -> str:
        return "Idref"

    def _titles(self, pub_graph, uri):
        title: Literal
        for title in pub_graph.objects(rdflib.term.URIRef(uri), DC.title):
            yield Title(
                value=remove_after_separator(title.value, "/"), language=title.language
            )

    async def _document_type(self, pub_graph, uri):
        for document_type in pub_graph.objects(rdflib.term.URIRef(uri), DC.type):
            uri, label = SudocDocumentTypeConverter().convert(str(document_type))
            yield await self._get_or_create_document_type_by_uri(uri, label)
