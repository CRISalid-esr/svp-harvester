from unittest.mock import patch

import rdflib.term
from rdflib import Graph, DC

from app.harvesters.idref.rdf_resolver import RdfResolver


@patch("app.harvesters.idref.resolver_http_client.ResolverHTTPClient.get")
async def test_fetch(mock_http_client, sudoc_rdf_xml_with_empty_date_fields):
    """
    GIVEN a RdfResolver instance and a Sudoc RDF XML with an empty dcterms:date and an empty dc:date
    WHEN the fetch method is called
    THEN it should return a Graph instance without triples with empty date values
    """
    # Arrange

    mock_http_client.return_value.get.return_value = (
        sudoc_rdf_xml_with_empty_date_fields
    )
    resolver = RdfResolver()

    # Act
    graph = await resolver.fetch("https://www.sudoc.fr/013451154.rdf")

    assert isinstance(graph, Graph)

    dc_date_predicate = DC.date
    dcterms_date_predicate = rdflib.term.URIRef("http://purl.org/dc/terms/date")

    # Query the graph for triples with the dc:date predicate and an empty object
    dc_date_triples = list(graph.triples((None, dc_date_predicate, rdflib.Literal(""))))
    # Assert that there are no such triples
    assert len(dc_date_triples) == 0, "Found triples with empty dc:date values"

    # Query the graph for triples with the dcterms:date predicate and an empty object
    dcterms_date_triples = list(
        graph.triples((None, dcterms_date_predicate, rdflib.Literal("")))
    )
    # Assert that there are no such triples
    assert (
        len(dcterms_date_triples) == 0
    ), "Found triples with empty dcterms:date values"
