"""Test the references API."""
from fastapi.testclient import TestClient


def test_create_retrieval_sync_with_idref(test_client: TestClient):
    """Test the create_retrieval_sync endpoint."""
    response = test_client.get("/api/v1/references?idref=123456789")
    assert response.status_code == 200


def test_create_retrieval_sync_error_with_name_only(test_client: TestClient):
    """
    Test validation error when calling create_retrieval_sync endpoint with name only.
    :param test_client:
    :return:
    """
    response = test_client.get("/api/v1/references?name=Bourdieu")
    assert response.status_code == 422


def test_fetch_references_async_with_name_and_idref(
    test_client: TestClient,
    person_with_name_and_idref_json,
):
    """Test the create_retrieval_sync endpoint."""
    response = test_client.post(
        "/api/v1/references/retrieval",
        json=person_with_name_and_idref_json,
    )
    assert response.status_code == 200


async def test_get_retrieval_result(
    test_client: TestClient,
    retrieval_db_model,
    async_session,
):
    """
    Test the get_retrieval_result endpoint.
    :param test_client:  test client
    :param retrieval_db_model:  retrieval from database
    :param async_session: async session
    :return:
    """
    async_session.add(retrieval_db_model)
    await async_session.commit()
    db_retrieval_id = retrieval_db_model.id
    response = test_client.get(
        f"/api/v1/references/retrieval/{db_retrieval_id}",
    )
    assert response.status_code == 200
