from unittest import mock

import pytest
import rdflib.term
from rdflib import Graph, DC

from app.harvesters.idref.rdf_resolver import RdfResolver
from app.harvesters.idref.resolver_http_client import ResolverHTTPClient


@pytest.fixture(name="fake_rdf_resolver_fixture", autouse=True)
def fixture_fake_rdf_resolver_fixture():
    """Disable the fake RDF resolver fetch method during tests."""
    return RdfResolver().fetch


@pytest.fixture(name="ResolverHTTPClient_mock", autouse=True)
def fixture_resolver_http_client_mock(sudoc_rdf_xml_with_empty_date_fields: str):
    """RDF resolver mock to detect fetch method calls."""
    with mock.patch.object(ResolverHTTPClient, "get") as mock_solve:
        mock_solve.return_value = sudoc_rdf_xml_with_empty_date_fields
        yield mock_solve


async def test_fetch():
    """
    GIVEN a RdfResolver instance and a Sudoc RDF XML with an empty dcterms:date and an empty dc:date
    WHEN the fetch method is called
    THEN it should return a Graph instance without triples with empty date values
    """

    resolver = RdfResolver()

    # Act
    graph = await resolver.fetch("https://www.sudoc.fr/test_url.rdf")

    assert isinstance(graph, Graph)

    dc_identifier_predicate = rdflib.term.URIRef("http://purl.org/dc/terms/identifier")
    dc_identifier_triples = list(graph.triples((None, dc_identifier_predicate, None)))
    expected_identifier = "027060918"
    assert (
        str(dc_identifier_triples[0][2]) == expected_identifier
    ), "The value of the dc:identifier predicate is not the expected one"

    dc_date_predicate = DC.date
    dcterms_date_predicate = rdflib.term.URIRef("http://purl.org/dc/terms/date")

    # Query the graph for triples with the dc:date predicate and an empty object
    dc_date_triples = list(graph.triples((None, dc_date_predicate, rdflib.Literal(""))))
    assert len(dc_date_triples) == 0, "Found triples with empty dc:date values"

    # Query the graph for triples with the dcterms:date predicate and an empty object
    dcterms_date_triples = list(
        graph.triples((None, dcterms_date_predicate, rdflib.Literal("")))
    )
    assert (
        len(dcterms_date_triples) == 0
    ), "Found triples with empty dcterms:date values"
