import asyncio
from os import environ
from typing import AsyncGenerator
from unittest import mock

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from app.db.models.concept import Concept as DbConcept
from app.db.session import engine, Base
from app.services.concepts.dereferencing_error import DereferencingError
from app.services.concepts.idref_concept_solver import IdRefConceptSolver
from tests.fixtures.common import *  # pylint: disable=unused-import, wildcard-import, unused-wildcard-import
from tests.fixtures.pydantic_entity_fixtures import *  # pylint: disable=unused-import, wildcard-import, unused-wildcard-import
from tests.fixtures.db_entity_fixtures import *  # pylint: disable=unused-import, wildcard-import, unused-wildcard-import
from tests.fixtures.hal_api_docs_fixtures import *  # pylint: disable=unused-import, wildcard-import, unused-wildcard-import
from tests.fixtures.idref_concept_rdf_docs_fixtures import *  # pylint: disable=unused-import, wildcard-import, unused-wildcard-import
from tests.fixtures.scanr_api_docs_fixtures import *  # pylint: disable=unused-import, wildcard-import, unused-wildcard-import
from tests.fixtures.science_plus_rdf_docs_fixtures import *  # pylint: disable=unused-import, wildcard-import, unused-wildcard-import
from tests.fixtures.sudoc_rdf_docs_fixtures import *  # pylint: disable=unused-import, wildcard-import, unused-wildcard-import
from tests.fixtures.idref_sparql_endpoint_docs_fixtures import *  # pylint: disable=unused-import, wildcard-import, unused-wildcard-import
from tests.fixtures.retrieval_fixtures import *  # pylint: disable=unused-import, wildcard-import, unused-wildcard-import
from tests.fixtures.harvesting_fixtures import *  # pylint: disable=unused-import, wildcard-import, unused-wildcard-import
from tests.fixtures.reference_fixtures import *  # pylint: disable=unused-import, wildcard-import, unused-wildcard-import
from tests.fixtures.reference_event_fixtures import *  # pylint: disable=unused-import, wildcard-import, unused-wildcard-import
from tests.fixtures.open_edition_doc_fixtures import *  # pylint: disable=unused-import, wildcard-import, unused-wildcard-import
from tests.fixtures.open_alex_docs_fixtures import *  # pylint: disable=unused-import, wildcard-import, unused-wildcard-import
from tests.fixtures.persee_rdf_docs_fixtures import *  # pylint: disable=unused-import, wildcard-import, unused-wildcard-import


environ["APP_ENV"] = "TEST"


@pytest.fixture(name="test_app")
def app() -> FastAPI:
    """Provide app as fixture"""
    # pylint: disable=import-outside-toplevel
    from app.main import SvpHarvester  # local import for testing purpose

    return SvpHarvester()


@pytest.fixture(name="test_client")
def fixture_test_client(test_app: FastAPI) -> TestClient:
    """Provide test client as fixture"""
    return TestClient(test_app)


@pytest.fixture(autouse=True, name="event_loop")
def fixture_event_loop():
    """Provide an event loop for all tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True, name="async_session")
async def fixture_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async db session for all tests"""
    session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session() as test_session:
        async with engine.begin() as test_connexion:
            await test_connexion.run_sync(Base.metadata.create_all)

        yield test_session

    async with engine.begin() as test_connexion:
        await test_connexion.run_sync(Base.metadata.drop_all)

    await engine.dispose()


def fake_idref_concept_solver(concept_id: str):
    """
    Fake idref concept solver for tests
    Raises DereferencingError except for a specific concept id

    :param concept_id: concept id to solve
    :return: fake concept
    """
    if concept_id == "http://www.idref.fr/allowed_concept_for_tests/id":
        return DbConcept(
            uri="http://www.idref.fr/allowed_concept_for_tests/id",
            labels=[
                Label(
                    value="Idref concept allowed for test",
                    language="en",
                    preferred=True,
                ),
                Label(
                    value="Concept Idref autorisé pour les tests",
                    language="fr",
                    preferred=True,
                ),
                Label(
                    value="Idref concept you can use for tests",
                    language="en",
                    preferred=False,
                ),
                Label(
                    value="Concept Idref que vous pouvez utiliser pour les tests",
                    language="fr",
                    preferred=False,
                ),
            ],
        )

    raise DereferencingError("Idref concept dereferencing not allowed during tests")


@pytest.fixture(name="mock_idref_concept_solver", autouse=True)
def fixture_mock_idref_concept_solver():
    """Hal harvester mock to detect is_relevant method calls."""
    with mock.patch.object(IdRefConceptSolver, "solve") as mock_solve:
        mock_solve.side_effect = fake_idref_concept_solver
        yield mock_solve
