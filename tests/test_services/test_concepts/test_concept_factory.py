from unittest import mock

import pytest

from app.services.concepts.concept_factory import ConceptFactory
from app.services.concepts.idref_concept_solver import IdRefConceptSolver
from app.services.concepts.unknown_authority_exception import UnknownAuthorityException
from app.services.concepts.wikidata_concept_solver import WikidataConceptSolver


@pytest.fixture(name="mock_idref_concept_solver_solve")
def fixture_mock_idref_concept_solver_solve():
    """
    Mocks the IdRefConceptSolver.solve method
    :return: mock
    """
    with mock.patch.object(IdRefConceptSolver, "solve") as mock_solve:
        yield mock_solve


@pytest.fixture(name="mock_wikidata_concept_solver_solve")
def fixture_mock_wikidata_concept_solver_solve():
    """
    Mocks the WikidataConceptSolver.solve method
    :return: mock
    """
    with mock.patch.object(WikidataConceptSolver, "solve") as mock_solve:
        yield mock_solve


# if we call the concept factory with a concept id beginning with http://www.idref.fr,
# without specifying a source,  then the idref solver is called
@pytest.mark.current
@pytest.mark.asyncio
async def test_concept_factory_idref_concept_id(mock_idref_concept_solver_solve):
    """
    GIVEN a concept factory
    WHEN calling it with a concept id beginning with http://www.idref.fr
    THEN the idref concept solver is called
    :param mock_idref_concept_solver_solve:
    :return:
    """
    concept_id = "http://www.idref.fr/033265077"
    await ConceptFactory.solve(concept_id)
    mock_idref_concept_solver_solve.assert_called_once_with(concept_id)


# if we call the concept factory with a concept number and specifying the idref source,
# then the idref solver is called
@pytest.mark.asyncio
@pytest.mark.current
async def test_concept_factory_idref_concept_number(mock_idref_concept_solver_solve):
    """
    GIVEN a concept factory
    WHEN calling it with a concept number and specifying the idref source
    THEN the idref concept solver is called
    :param mock_idref_concept_solver_solve:
    :return:
    """
    concept_id = "033265077"
    await ConceptFactory.solve(concept_id, ConceptFactory.ConceptSources.IDREF)
    mock_idref_concept_solver_solve.assert_called_once_with(concept_id)


# if we call the concept factory with a concept number and specifying the wikidata source,
# then the wikidata solver is called
@pytest.mark.asyncio
@pytest.mark.current
async def test_concept_factory_wikidata_concept_number(
    mock_wikidata_concept_solver_solve,
):
    """
    GIVEN a concept factory
    WHEN calling it with a concept number and specifying the wikidata source
    THEN the wikidata concept solver is called
    :param mock_wikidata_concept_solver_solve:
    :return:
    """
    concept_id = "Q1234"
    await ConceptFactory.solve(concept_id, ConceptFactory.ConceptSources.WIKIDATA)
    mock_wikidata_concept_solver_solve.assert_called_once_with(concept_id)


# if we call the concept factory with a concept id beginning with http://www.wikidata.org,
# without specifying a source,  then the wikidata solver is called
@pytest.mark.asyncio
@pytest.mark.current
async def test_concept_factory_wikidata_concept_id(mock_wikidata_concept_solver_solve):
    """
    GIVEN a concept factory
    WHEN calling it with a concept id beginning with http://www.wikidata.org
    THEN the wikidata concept solver is called
    :param mock_wikidata_concept_solver_solve:
    :return:
    """
    concept_id = "http://www.wikidata.org/entity/Q1234"
    await ConceptFactory.solve(concept_id)
    mock_wikidata_concept_solver_solve.assert_called_once_with(concept_id)


# if we call the concept factory with a fake concept id, UnknownAuthorityException is raised
@pytest.mark.asyncio
@pytest.mark.current
async def test_concept_factory_unknown_authority_exception():
    """
    GIVEN a concept factory
    WHEN calling it with a fake concept id
    THEN UnknownAuthorityException is raised
    :return:
    """
    concept_id = "http://www.fake.fr/033265077"
    with pytest.raises(UnknownAuthorityException):
        await ConceptFactory.solve(concept_id)
