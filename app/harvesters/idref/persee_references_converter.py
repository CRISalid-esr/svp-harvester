from typing import AsyncGenerator

import rdflib
from rdflib import DCTERMS, FOAF, RDF, Graph, Literal, Namespace, URIRef

from app.db.models.document_type import DocumentType
from app.db.models.reference_identifier import ReferenceIdentifier
from app.db.models.reference import Reference
from app.db.models.title import Title
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.idref.abes_rdf_references_converter import (
    AbesRDFReferencesConverter,
)
from app.harvesters.idref.persee_qualities_converter import PerseeQualitiesConverter
from app.harvesters.idref.rdf_resolver import RdfResolver
from app.harvesters.rdf_harvester_raw_result import RdfHarvesterRawResult


class PerseeReferencesConverter(AbesRDFReferencesConverter):
    """
    Converts raw data from Persee to a normalised Reference object
    """

    RDF_BIBO = "http://purl.org/ontology/bibo/"

    async def convert(self, raw_data: RdfHarvesterRawResult) -> Reference:
        new_ref = await super().convert(raw_data)
        pub_graph: Graph = raw_data.payload
        uri = raw_data.source_identifier

        async for document_type in self._document_type(pub_graph, uri):
            new_ref.document_type.append(document_type)

        await self._add_contributions(pub_graph, new_ref)

        return new_ref

    def _add_reference_identifiers(self, pub_graph, uri):
        yield ReferenceIdentifier(value=uri, type="uri")
        for identifier in pub_graph.objects(
            rdflib.term.URIRef(uri), URIRef(self.RDF_BIBO + "doi")
        ):
            yield ReferenceIdentifier(value=identifier, type="doi")

    async def _add_contributions(self, pub_graph, new_ref):
        contribution_informations = []
        marcrel = Namespace("http://id.loc.gov/vocabulary/relators/")
        query = f"""
                        SELECT ?predicate ?object 
                        WHERE {{
                            ?subject ?predicate ?object .
                            FILTER(STRSTARTS(STR(?predicate), "{str(marcrel)}")).
                        }}
                    """
        results = pub_graph.query(query)
        for role, identifier in results:
            role = role.split("/")[-1]
            graph = await RdfResolver().fetch(identifier)
            contributor_name = ""
            for name in graph.objects(identifier, FOAF.name):
                contributor_name = name
            contribution_informations.append(
                AbstractReferencesConverter.ContributionInformations(
                    role=PerseeQualitiesConverter.convert(role),
                    identifier=identifier,
                    name=contributor_name,
                    rank=None,
                )
            )
        async for contribution in self._contributions(
            contribution_informations=contribution_informations, source="persee"
        ):
            new_ref.contributions.append(contribution)

    async def _document_type(
        self, pub_graph, uri
    ) -> AsyncGenerator[DocumentType, None]:
        document_type_cache = {}
        document_type_uri: URIRef
        for document_type_uri in pub_graph.objects(rdflib.term.URIRef(uri), RDF.type):
            label = str(document_type_uri).rsplit("/", maxsplit=1)[-1]
            document_type_key = (document_type_uri, label)
            if document_type_key in document_type_cache:
                yield document_type_cache[document_type_key]
                continue

            document_type_db = await self._get_or_create_document_type_by_uri(
                uri=document_type_uri, label=label
            )
            document_type_cache[document_type_key] = document_type_db
            yield document_type_db

    def _titles(self, pub_graph, uri):
        title: Literal
        for title in pub_graph.objects(rdflib.term.URIRef(uri), DCTERMS.title):
            lng = title.language
            if not title.language:
                for lng in pub_graph.objects(rdflib.term.URIRef(uri), DCTERMS.language):
                    lng = lng.value
                    break
            yield Title(value=title.value, language=lng)
