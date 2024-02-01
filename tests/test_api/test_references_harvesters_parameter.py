"""Test that references API creates Retrieval in database."""

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration

REFERENCES_RETRIEVAL_API_PATH = "/api/v1/references/retrieval"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "requested_harvesters, number_of_harvesters",
    [
        (None, 3),
        ([], 0),
        (["hal"], 1),
        (["hal", "idref"], 2),
    ],
)
async def test_fetch_references_async_with_history_safe_or_unsafe(  # pylint: disable=too-many-statements
    test_client: TestClient,
    person_with_name_and_orcid_json,
    requested_harvesters,
    number_of_harvesters,
):
    """
    GIVEN a test client and a person with a HAL I id
    WHEN the references retrieval API is called with a limited set of harvesters
    THEN check that only the requested harvesters are instantiated by the retrieval service



    :param test_client:
    :param person_with_name_and_id_hal_i_json:
    :param hal_api_docs_for_researcher_version_1:
    :param hal_api_docs_for_researcher_version_2:
    :return:
    """

    response = test_client.post(
        REFERENCES_RETRIEVAL_API_PATH,
        json={
            "person": person_with_name_and_orcid_json,
            "events": ["created", "updated", "deleted", "unchanged"],
            "harvesters": requested_harvesters,
        },
    )
    assert response.status_code == 200
    json_response = response.json()
    retrieval_url = json_response["retrieval_url"]
    assert retrieval_url is not None
    response = test_client.get(retrieval_url)
    assert response.status_code == 200
    json_response = response.json()
    assert len(json_response["harvestings"]) == number_of_harvesters
    # assert that each harvesting was present in the requested harvesters
    if requested_harvesters is not None:
        for harvesting in json_response["harvestings"]:
            assert harvesting["harvester"] in requested_harvesters
