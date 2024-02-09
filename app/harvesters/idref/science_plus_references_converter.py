import rdflib
from rdflib import Literal, DCTERMS
from app.db.models.publication_identifier import PublicationIdentifier
from app.db.models.reference import Reference

from app.db.models.title import Title
from app.harvesters.idref.abes_rdf_references_converter import (
    AbesRDFReferencesConverter,
)
from app.harvesters.rdf_harvester_raw_result import RdfHarvesterRawResult


class SciencePlusReferencesConverter(AbesRDFReferencesConverter):
    """
    Converts raw data from SciencePlus to a normalised Reference object
    """

    async def convert(self, raw_data: RdfHarvesterRawResult) -> Reference:
        new_ref = await super().convert(raw_data)

        if raw_data.doi:
            new_ref.identifiers.append(self._add_doi_identifier(raw_data.doi))

        return new_ref

    def _titles(self, pub_graph, uri):
        title: Literal
        for title in pub_graph.objects(rdflib.term.URIRef(uri), DCTERMS.title):
            yield Title(value=title.value, language=title.language)

    def _add_doi_identifier(self, doi: str):
        return PublicationIdentifier(value=doi, type="doi")
