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
    persee_rdf_result_for_journal: Graph,
    science_plus_rdf_result_for_journal: Graph,
    science_plus_rdf_result_for_issue: Graph,
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
        if document_uri == "https://data.persee.fr/issue/hista_0992-2059_1998_num_42_1":
            return persee_rdf_result_for_journal
        if (
            document_uri
            == "https://scienceplus.abes.fr/sparql?query=define+sql%3Adescribe-mode+%22CBD%22++DESCRIBE+%3Chttp%3A%2F%2Fhub.abes.fr%2Fspringer%2Fperiodical%2F10571%2Fw%3E&output=application%2Frdf%2Bxml"
        ):
            return science_plus_rdf_result_for_journal
        if (
            document_uri
            == "https://scienceplus.abes.fr/sparql?query=define+sql%3Adescribe-mode+%22CBD%22++DESCRIBE+%3Chttp%3A%2F%2Fhub.abes.fr%2Fspringer%2Fperiodical%2F10571%2F1992%2Fvolume_12%2Fissue_1%2Fw%3E&output=application%2Frdf%2Bxml"
        ):
            return science_plus_rdf_result_for_issue
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
