import rdflib
from rdflib import Literal, DCTERMS

from app.db.models.title import Title
from app.harvesters.idref.abes_rdf_references_converter import (
    AbesRDFReferencesConverter,
)


class SciencePlusReferencesConverter(AbesRDFReferencesConverter):
    """
    Converts raw data from SciencePlus to a normalised Reference object
    """

    def _titles(self, pub_graph, uri):
        title: Literal
        for title in pub_graph.objects(rdflib.term.URIRef(uri), DCTERMS.title):
            yield Title(value=title.value, language=title.language)
