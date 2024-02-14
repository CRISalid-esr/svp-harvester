from unittest import mock
import pytest
from app.db.models.concept import Concept as DbConcept
from app.db.models.label import Label

from app.services.concepts.wikidata_concept_solver import WikidataConceptSolver


def fake_wikidata_concept_solver(uri: str):
    """
    Fake wikidata concept solver
    :param concept_id: concept id
    :return: fake concept
    """
    if uri == "http://www.wikidata.org/entity/test_id":
        return DbConcept(
            uri="http://www.wikidata.org/entity/test_id",
            labels=[
                Label(value="Test concept", language="en", preferred=True),
                Label(value="Concept de test", language="fr", preferred=True),
                Label(value="Concepto de test", language="es", preferred=False),
            ],
        )


@pytest.fixture(name="mock_wikidata_concept_solver", autouse=True)
def fixture_mock_wikidata_concept_solver():
    """
    Mock the wikidata concept solver with fake concept solver
    """
    with mock.patch.object(WikidataConceptSolver, "solve") as mock_solve:
        mock_solve.side_effect = fake_wikidata_concept_solver
        yield mock_solve
