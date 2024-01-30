import hashlib
from typing import AsyncGenerator
from rdflib import DCTERMS, FOAF, RDF, Graph, Literal, Namespace, URIRef
import rdflib
from app.db.daos.contributor_dao import ContributorDAO
from app.db.models.abstract import Abstract
from app.db.models.contribution import Contribution
from app.db.models.contributor import Contributor
from app.db.models.document_type import DocumentType
from app.db.models.reference import Reference
from app.db.models.title import Title
from app.db.session import async_session
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.idref.persee_qualities_converter import PerseeQualitiesConverter
from app.harvesters.idref.rdf_resolver import RdfResolver
from app.harvesters.rdf_harvester_raw_result import RdfHarvesterRawResult


class PerseeReferencesConverter(AbstractReferencesConverter):
    """
    Converts raw data from Persee to a normalised Reference object
    """

    async def convert(self, raw_data: RdfHarvesterRawResult) -> Reference:
        new_ref = Reference()
        pub_graph: Graph = raw_data.payload

        uri = raw_data.source_identifier
        new_ref.source_identifier = uri

        new_ref.titles = [
            Title(value=title.value, language=title.language)
            for title in self._titles(pub_graph, uri)
        ]

        new_ref.abstracts = [abstract for abstract in self._abstracts(pub_graph, uri)]

        async for document_type in self._document_type(pub_graph, uri):
            new_ref.document_type.append(document_type)

        async for contribution in self._contributions(pub_graph):
            new_ref.contributions.append(contribution)

        new_ref.hash = self._hash_from_rdf_graph(pub_graph, uri)
        return new_ref

    async def _contributions(
        self, pub_graph: Graph
    ) -> AsyncGenerator[Contribution, None]:
        async with async_session() as session:
            marcrel = Namespace("http://id.loc.gov/vocabulary/relators/")

            query = f"""
                SELECT ?predicate ?object 
                WHERE {{
                    ?subject ?predicate ?object .
                    FILTER(STRSTARTS(STR(?predicate), "{str(marcrel)}")).
                }}
            """
            results = pub_graph.query(query)
            for role, person in results:
                role = role.split("/")[-1]
                g = await RdfResolver().fetch(person)
                contributor_name = None
                for name in g.objects(person, FOAF.name):
                    contributor_name = name
                db_contributor = await ContributorDAO(
                    session
                ).get_by_source_and_identifier("persee", str(person))
                if db_contributor is None:
                    db_contributor = await ContributorDAO(
                        session
                    ).get_by_source_and_name("persee", contributor_name)
                if db_contributor is None:
                    db_contributor = Contributor(
                        name=contributor_name,
                        source="persee",
                        source_identifier=str(person),
                    )
                yield Contribution(
                    contributor=db_contributor,
                    role=PerseeQualitiesConverter.convert(role),
                )

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
            lan = title.language
            if not title.language:
                for lan in pub_graph.objects(rdflib.term.URIRef(uri), DCTERMS.language):
                    lan = lan.value
                    break
            yield Title(value=title.value, language=lan)

    def _abstracts(self, pub_graph, uri):
        abstract: Literal
        for abstract in pub_graph.objects(rdflib.term.URIRef(uri), DCTERMS.abstract):
            yield Abstract(value=abstract.value, language=abstract.language)

    def _hash_from_rdf_graph(self, pub_graph: Graph, uri: str) -> str:
        graph_as_dict = {
            str(p): str(o)
            for s, p, o in pub_graph.triples((rdflib.term.URIRef(uri), None, None))
        }
        return hashlib.sha256(str(graph_as_dict).encode()).hexdigest()
