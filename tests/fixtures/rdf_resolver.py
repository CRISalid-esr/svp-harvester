from unittest import mock
import pytest
from rdflib import Graph

from app.harvesters.idref.rdf_resolver import RdfResolver
from app.services.concepts.dereferencing_error import DereferencingError


@pytest.fixture(name="fake_rdf_resolver_fixture")
def fixture_fake_rdf_resolver_fixture(
    sudoc_rdf_graph_for_doc: Graph,
    persee_rdf_graph_for_person: Graph,
    sudoc_rdf_result_for_journal: Graph,
):

    def fake_rdf_resolver(document_uri: str, output_format: str = "xml") -> Graph:
        """
        Fake rdf resolver fetch
        :param document_uri: document uri
        :param output_format: output format
        :return: fake graph
        """
        document_uri = str(document_uri)
        if document_uri == "https://www.sudoc.fr/193726130.rdf":
            return sudoc_rdf_graph_for_doc
        if document_uri == "http://data.persee.fr/authority/214267#Person":
            return persee_rdf_graph_for_person
        if document_uri == "https://www.sudoc.fr/013451154.rdf":
            return sudoc_rdf_result_for_journal
        raise DereferencingError(
            f"Rdf resolver fetch not allowed during tests for {document_uri}"
        )

    return fake_rdf_resolver


@pytest.fixture(name="rdf_resolver_mock", autouse=True)
def fixture_rdf_resolver_mock(fake_rdf_resolver_fixture):
    """RDF resolver mock to detect fetch method calls."""
    with mock.patch.object(RdfResolver, "fetch") as mock_solve:
        mock_solve.side_effect = fake_rdf_resolver_fixture
        yield mock_solve
