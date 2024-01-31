import rdflib
from rdflib import DC, Literal

from app.db.models.title import Title
from app.harvesters.idref.abes_rdf_references_converter import (
    AbesRDFReferencesConverter,
)
from app.utilities.string_utilities import remove_after_separator


class SudocReferencesConverter(AbesRDFReferencesConverter):
    """
    Converts raw data from Sudoc to a normalised Reference object
    """

    def _titles(self, pub_graph, uri):
        title: Literal
        for title in pub_graph.objects(rdflib.term.URIRef(uri), DC.title):
            yield Title(
                value=remove_after_separator(title.value, "/"), language=title.language
            )
