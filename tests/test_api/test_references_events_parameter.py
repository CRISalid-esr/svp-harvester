"""Test that references API creates Retrieval in database."""
from unittest import mock

import aiohttp
import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration

REFERENCES_RETRIEVAL_API_PATH = "/api/v1/references/retrieval"


@pytest.mark.asyncio
async def test_fetch_references_async_with_all_event_types(
    test_client: TestClient,
    person_with_name_and_id_hal_i_json,
    hal_api_docs_for_researcher_version_1,
    hal_api_docs_for_researcher_version_2,
):
    """
    GIVEN a test client and a person with name and id
    WHEN the references retrieval endpoint is called twice with all event types
    AND the second call has a new version of the results
    THEN check that all kinds of events are retrieved : created, updated, deleted, unchanged

    :param test_client:
    :param person_with_name_and_id_hal_i_json:
    :param hal_api_docs_for_researcher_version_1:
    :param hal_api_docs_for_researcher_version_2:
    :return:
    """
    with mock.patch.object(aiohttp.ClientSession, "get") as aiohttp_client_session_get:
        aiohttp_client_session_get.return_value.__aenter__.return_value.status = 200
        aiohttp_client_session_get.return_value.__aenter__.return_value.json.return_value = (
            hal_api_docs_for_researcher_version_1
        )

        response = test_client.post(
            REFERENCES_RETRIEVAL_API_PATH,
            json={
                "person": person_with_name_and_id_hal_i_json,
                "events": ["created", "updated", "deleted", "unchanged"],
            },
        )
        assert response.status_code == 200
        json_response = response.json()
        retrieval_url = json_response["retrieval_url"]
        assert retrieval_url is not None
        response = test_client.get(retrieval_url)
        assert response.status_code == 200
        json_response = response.json()
        assert json_response["harvestings"][0]["state"] == "completed"
        assert json_response["harvestings"][0]["harvester"] == "hal"
        # it has 3 reference events
        assert len(json_response["harvestings"][0]["reference_events"]) == 3
        # all 3 reference events are of type created
        assert all(
            reference_event["type"] == "created"
            for reference_event in json_response["harvestings"][0]["reference_events"]
        )
        assert any(
            reference_event["reference"]["titles"][0]["value"]
            == "The metaphorical structuring of kinship in Latin"
            for reference_event in json_response["harvestings"][0]["reference_events"]
        )
    # Now relaunch the same retrieval with a new version of the results
    with mock.patch.object(aiohttp.ClientSession, "get") as aiohttp_client_session_get:
        aiohttp_client_session_get.return_value.__aenter__.return_value.status = 200
        aiohttp_client_session_get.return_value.__aenter__.return_value.json.return_value = (
            hal_api_docs_for_researcher_version_2
        )
        response = test_client.post(
            REFERENCES_RETRIEVAL_API_PATH,
            json={
                "person": person_with_name_and_id_hal_i_json,
                "events": ["created", "updated", "deleted", "unchanged"],
            },
        )
        assert response.status_code == 200
        json_response = response.json()
        retrieval_url = json_response["retrieval_url"]
        assert retrieval_url is not None
        response = test_client.get(retrieval_url)
        assert response.status_code == 200
        json_response = response.json()
        assert json_response["harvestings"][0]["state"] == "completed"
        assert json_response["harvestings"][0]["harvester"] == "hal"
        # it has 4 reference events
        assert len(json_response["harvestings"][0]["reference_events"]) == 4
        # among them, exactly one has the reference with source identifier 1719671 and is unchanged
        assert (
            len(
                [
                    reference_event
                    for reference_event in json_response["harvestings"][0][
                        "reference_events"
                    ]
                    if reference_event["reference"]["source_identifier"] == "1719671"
                    and reference_event["type"] == "unchanged"
                ]
            )
            == 1
        )
        # among them, exactly one has the reference with source identifier 3002983 and is created
        assert (
            len(
                [
                    reference_event
                    for reference_event in json_response["harvestings"][0][
                        "reference_events"
                    ]
                    if reference_event["reference"]["source_identifier"] == "3002983"
                    and reference_event["type"] == "created"
                ]
            )
            == 1
        )
        # among them, exactly one has the reference with source identifier 3002970 and is deleted
        assert (
            len(
                [
                    reference_event
                    for reference_event in json_response["harvestings"][0][
                        "reference_events"
                    ]
                    if reference_event["reference"]["source_identifier"] == "3002970"
                    and reference_event["type"] == "deleted"
                ]
            )
            == 1
        )
        # among them, exactly one has the reference with source identifier 2091947 and is updated
        assert (
            len(
                [
                    reference_event
                    for reference_event in json_response["harvestings"][0][
                        "reference_events"
                    ]
                    if reference_event["reference"]["source_identifier"] == "2091947"
                    and reference_event["type"] == "updated"
                ]
            )
            == 1
        )
