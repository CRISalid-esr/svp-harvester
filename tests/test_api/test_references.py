"""Test the references API."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.identifier import Identifier
from app.db.models.person import Person
from app.db.models.reference_event import ReferenceEvent

pytestmark = pytest.mark.integration

REFERENCES_RETRIEVAL_API_PATH = "/api/v1/references/retrieval"


def test_create_retrieval_sync_with_idref(test_client: TestClient):
    """Test the create_retrieval_sync endpoint."""
    response = test_client.get("/api/v1/references?idref=123456789")
    assert response.status_code == 200


def test_create_retrieval_sync_valid_with_name_only(test_client: TestClient):
    """
    Test validation when calling create_retrieval_sync endpoint with name only.
    :param test_client:
    :return:
    """
    response = test_client.get("/api/v1/references?name=Bourdieu")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_fetch_references_async_with_name_and_idref(
    test_client: TestClient,
    person_with_name_and_idref_json,
    async_session: AsyncSession,
):
    """Test the create_retrieval_sync endpoint."""
    response = test_client.post(
        REFERENCES_RETRIEVAL_API_PATH,
        json={"person": person_with_name_and_idref_json},
    )
    assert response.status_code == 200
    person_name = person_with_name_and_idref_json["name"]
    person_idref = person_with_name_and_idref_json["identifiers"][0]["value"]
    # find the person in the database by idref
    person = (
        (
            await async_session.execute(
                select(Person)
                .join(Identifier)
                .filter(Identifier.value == person_idref and Identifier.type == "idref")
            )
        )
        .unique()
        .scalar_one_or_none()
    )
    assert person is not None
    assert person.name == person_name


def test_fetch_references_async_with_name_and_unknown_identifier_type(
    test_client: TestClient,
    person_with_name_and_unknown_identifier_type_json,
):
    """Test the create_retrieval_sync endpoint."""
    response = test_client.post(
        REFERENCES_RETRIEVAL_API_PATH,
        json={"person": person_with_name_and_unknown_identifier_type_json},
    )
    assert response.status_code == 422


async def test_get_retrieval_result_response_ok(
    test_client: TestClient,
    retrieval_db_model_for_person_with_idref,
    async_session: AsyncSession,
):
    """
    Test the get_retrieval_result endpoint.
    :param test_client:  test client
    :param retrieval_db_model_for_person_with_idref:  retrieval from database
    :param async_session: async session
    :return:
    """
    async_session.add(retrieval_db_model_for_person_with_idref)
    await async_session.commit()
    db_retrieval_id = retrieval_db_model_for_person_with_idref.id
    response = test_client.get(
        f"/api/v1/references/retrieval/{db_retrieval_id}",
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_retrieval_result_with_subjects_without_uri(
    test_client: TestClient,
    reference_event_db_model: ReferenceEvent,
    async_session: AsyncSession,
):
    """
    Test the get_retrieval_result endpoint.
    :param test_client:  test client
    :param reference_event_db_model:  reference event from database
    :param async_session: async session
    :return:
    """
    reference_event_db_model.reference.subjects[0].uri = None
    async_session.add(reference_event_db_model)
    await async_session.commit()
    db_retrieval_id = reference_event_db_model.harvesting.retrieval.id
    response = test_client.get(
        f"/api/v1/references/retrieval/{db_retrieval_id}",
    )
    assert response.status_code == 200
    json_response = response.json()
    assert (
        json_response["harvestings"][0]["reference_events"][0]["reference"]["subjects"][
            0
        ]["pref_labels"][0]["value"]
        == "label"
    )
    assert (
        json_response["harvestings"][0]["reference_events"][0]["reference"]["subjects"][
            0
        ]["pref_labels"][0]["language"]
        == "fr"
    )


@pytest.mark.asyncio
async def test_get_retrieval_result(
    test_client: TestClient,
    reference_event_db_model: ReferenceEvent,
    async_session: AsyncSession,
):
    """
    Test the get_retrieval_result endpoint.
    :param test_client:  test client
    :param reference_event_db_model:  reference event from database
    :param async_session: async session
    :return:
    """
    async_session.add(reference_event_db_model)
    await async_session.commit()
    db_retrieval_id = reference_event_db_model.harvesting.retrieval.id
    response = test_client.get(
        f"/api/v1/references/retrieval/{db_retrieval_id}",
    )
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["harvestings"][0]["harvester"] == "idref"
    assert len(json_response["harvestings"][0]["reference_events"]) == 1
    assert json_response["harvestings"][0]["reference_events"][0]["type"] == "created"
    assert (
        json_response["harvestings"][0]["reference_events"][0]["reference"][
            "source_identifier"
        ]
        == "123456789"
    )
    assert (
        json_response["harvestings"][0]["reference_events"][0]["reference"]["titles"][
            0
        ]["value"]
        == "title"
    )
    assert (
        json_response["harvestings"][0]["reference_events"][0]["reference"]["titles"][
            0
        ]["language"]
        == "fr"
    )
    assert (
        json_response["harvestings"][0]["reference_events"][0]["reference"]["subjects"][
            0
        ]["uri"]
        == "http://uri"
    )
    assert (
        json_response["harvestings"][0]["reference_events"][0]["reference"]["subjects"][
            0
        ]["labels"][0]["value"]
        == "label"
    )
    assert (
        json_response["harvestings"][0]["reference_events"][0]["reference"]["subjects"][
            0
        ]["labels"][0]["language"]
        == "fr"
    )


@pytest.mark.asyncio
async def test_post_request_creates_person_with_name_in_db(
    test_client: TestClient,
    person_with_name_and_idref_json,
    async_session: AsyncSession,
):
    """
    Test that a POST request to the retrieval endpoint creates a person with name in the database.

    :param test_client: test client
    :param person_with_name_and_idref_json: person with name and IDREF in JSON format
    :param async_session: async session
    :return: None
    """
    response = test_client.post(
        REFERENCES_RETRIEVAL_API_PATH,
        json={"person": person_with_name_and_idref_json},
    )
    assert response.status_code == 200
    person = await async_session.execute(
        select(Person)
        .join(Identifier)
        .where(Identifier.type == "idref")
        .where(
            Identifier.value
            == person_with_name_and_idref_json.get("identifiers")[0].get("value")
        )
    )
    assert person.scalars().first().name == person_with_name_and_idref_json.get("name")


@pytest.mark.asyncio
async def test_a_second_post_request_updates_the_name_of_the_person_in_db(
    test_client: TestClient,
    person_with_name_and_idref_json,
    async_session: AsyncSession,
):
    """
    GIVEN a first POST request to the retrieval endpoint with a person with name and IDREF
    WHEN a second POST request is made with the same IDREF and a different name
    THEN the name of the person in the database is updated.

    :param test_client: test client
    :param person_with_name_and_idref_json: person with name and IDREF in JSON format
    :param async_session: async session
    :return: None
    """
    response = test_client.post(
        REFERENCES_RETRIEVAL_API_PATH,
        json={"person": person_with_name_and_idref_json},
    )
    assert response.status_code == 200
    person = await async_session.execute(
        select(Person)
        .join(Identifier)
        .where(Identifier.type == "idref")
        .where(
            Identifier.value
            == person_with_name_and_idref_json.get("identifiers")[0].get("value")
        )
    )
    assert person.scalars().first().name == person_with_name_and_idref_json.get("name")
    person_with_name_and_idref_json["name"] = "new name"
    response = test_client.post(
        REFERENCES_RETRIEVAL_API_PATH,
        json={"person": person_with_name_and_idref_json},
    )
    assert response.status_code == 200
    person = await async_session.execute(
        select(Person)
        .join(Identifier)
        .where(Identifier.type == "idref")
        .where(
            Identifier.value
            == person_with_name_and_idref_json.get("identifiers")[0].get("value")
        )
    )
    assert person.scalars().first().name == "new name"
