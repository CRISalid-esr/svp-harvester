import logging
from unittest import mock

import pytest
import rdflib.term
from rdflib import Graph, DC

from app.harvesters.exceptions.unexpected_format_exception import (
    UnexpectedFormatException,
)
from app.harvesters.idref.rdf_resolver import RdfResolver
from app.harvesters.idref.resolver_http_client import ResolverHTTPClient


@pytest.fixture(name="fake_rdf_resolver_fixture", autouse=True)
def fixture_fake_rdf_resolver_fixture():
    """Disable the fake RDF resolver fetch method during tests."""
    return RdfResolver().fetch


@pytest.fixture(name="resolver_http_client_mock")
def fixture_resolver_http_client_mock(sudoc_rdf_xml_with_date_fields: str):
    """RDF resolver mock to detect fetch method calls."""
    with mock.patch.object(ResolverHTTPClient, "get") as mock_solve:
        mock_solve.return_value = sudoc_rdf_xml_with_date_fields
        yield mock_solve


@pytest.fixture(name="resolver_http_client_mock_with_empty_response")
def fixture_resolver_http_client_mock_with_empty_response():
    """RDF resolver mock to detect fetch method calls."""
    with mock.patch.object(ResolverHTTPClient, "get") as mock_solve:
        mock_solve.return_value = None
        yield mock_solve


async def test_fetch(resolver_http_client_mock):  # pylint: disable=unused-argument
    """
    GIVEN a RdfResolver instance and a Sudoc RDF XML with an empty dcterms:date and an empty dc:date
    WHEN the fetch method is called
    THEN it should return a Graph instance without triples with empty date values
    """

    resolver = RdfResolver()

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

    dc_date_triples = list(graph.triples((None, dc_date_predicate, rdflib.Literal(""))))
    assert len(dc_date_triples) == 0, "Found triples with empty dc:date values"

    dcterms_date_triples = list(
        graph.triples((None, dcterms_date_predicate, rdflib.Literal("")))
    )
    assert (
        len(dcterms_date_triples) == 0
    ), "Found triples with empty dcterms:date values"


async def test_fetch_with_empty_response(
    resolver_http_client_mock_with_empty_response,  # pylint: disable=unused-argument
):
    """
    GIVEN a RdfResolver instance and an empty response from the RDF resolver
    WHEN the fetch method is called
    THEN it should raise an UnexpectedFormatException
    """

    resolver = RdfResolver()
    test_url = "https://www.sudoc.fr/test_url.rdf"
    with pytest.raises(UnexpectedFormatException) as excinfo:
        await resolver.fetch(test_url)

    assert f"Empty response from {test_url} : None" in str(excinfo.value)


@pytest.fixture(name="resolver_http_client_mock_with_persee_wrong_dates")
def fixture_resolver_http_client_mock_with_persee_bst(
    persee_rdf_xml_person_with_wrong_dates,
):
    with mock.patch.object(ResolverHTTPClient, "get") as mock_get:
        mock_get.return_value = persee_rdf_xml_person_with_wrong_dates
        yield mock_get


import pytest


async def test_fetch_should_not_emit_invalid_isoformat_errors(
    resolver_http_client_mock_with_persee_wrong_dates,  # pylint: disable=unused-argument
    caplog,
    capsys,
):
    """
    GIVEN a RdfResolver instance and a Persee RDF XML with invalid date formats containing BST markers
    WHEN the fetch method is called
    THEN it should not emit 'Invalid isoformat string' conversion errors in the logs or stderr

    Explanation:
        If the RDF contains a date like <dcterms:date>2024-09-07BST21:13:02</dcterms:date>,
        rdflib may attempt to convert it to a datetime object and fail,
        emitting an error message like 'Invalid isoformat string' in the logs or stderr.
        After patching the _clean_response_text method to normalize such date formats,
        these errors should no longer occur.
    """
    resolver = RdfResolver()

    # Capture rdflib logs (they often use the standard logging module)
    caplog.set_level(logging.WARNING)

    graph = await resolver.fetch("https://data.persee.fr/authority/385736.rdf")
    assert isinstance(graph, Graph)

    # Some rdflib versions log the conversion failure...
    logged = "\n".join(r.getMessage() for r in caplog.records)

    # ...others may dump the traceback to stderr.
    captured = capsys.readouterr()
    stderr = captured.err or ""

    combined = logged + "\n" + stderr

    assert "Invalid isoformat string" not in combined, combined
    assert "Failed to convert Literal lexical form to value" not in combined, combined
