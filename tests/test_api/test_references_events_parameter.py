"""Test that references API creates Retrieval in database."""
from asyncio import sleep
from unittest import mock

import aiohttp
import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration

REFERENCES_RETRIEVAL_API_PATH = "/api/v1/references/retrieval"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "event_types_1,event_types_2,num_results_1,num_results_2",
    [
        (
            ["created", "updated", "deleted", "unchanged"],
            ["created", "updated", "deleted", "unchanged"],
            3,
            4,
        ),
        (
            ["created", "updated", "deleted", "unchanged"],
            ["created", "updated", "deleted"],
            3,
            3,
        ),
        (["created", "updated", "deleted", "unchanged"], ["created", "updated"], 3, 2),
        (["created", "updated", "deleted", "unchanged"], ["created"], 3, 1),
        (["created", "updated", "deleted", "unchanged"], ["updated"], 3, 1),
        (["created", "updated", "deleted", "unchanged"], ["deleted"], 3, 1),
    ],
)
async def test_fetch_references_async_with_all_event_types(
    test_client: TestClient,
    person_with_name_and_id_hal_i_json,
    hal_api_docs_for_researcher_version_1,
    hal_api_docs_for_researcher_version_2,
    event_types_1,
    event_types_2,
    num_results_1,
    num_results_2,
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
                "events": event_types_1,
            },
        )
        assert response.status_code == 200
        json_response = response.json()
        retrieval_url = json_response["retrieval_url"]
        assert retrieval_url is not None
        # while state is not completed, continue querying
        json_response = None
        json_response = {}
        while (
            not json_response or json_response["harvestings"][0]["state"] != "completed"
        ):
            json_response and sleep(0.1)
            response = test_client.get(retrieval_url)
            assert response.status_code == 200
            json_response = response.json()
        assert json_response["harvestings"][0]["harvester"] == "hal"
        assert len(json_response["harvestings"][0]["reference_events"]) == num_results_1
        # all reference events are of type created
        assert all(
            reference_event["type"] == "created"
            for reference_event in json_response["harvestings"][0]["reference_events"]
        )
        if "created" in event_types_1:
            assert any(
                reference_event["reference"]["titles"][0]["value"]
                == "The metaphorical structuring of kinship in Latin"
                for reference_event in json_response["harvestings"][0][
                    "reference_events"
                ]
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
                "events": event_types_2,
            },
        )
        assert response.status_code == 200
        json_response = response.json()
        retrieval_url = json_response["retrieval_url"]
        assert retrieval_url is not None
        # while state is not completed, continue querying
        json_response = None
        json_response = {}
        while (
            not json_response or json_response["harvestings"][0]["state"] != "completed"
        ):
            json_response and sleep(0.1)
            response = test_client.get(retrieval_url)
            assert response.status_code == 200
            json_response = response.json()
        assert json_response["harvestings"][0]["harvester"] == "hal"
        # it has 4 reference events
        assert len(json_response["harvestings"][0]["reference_events"]) == num_results_2
        # among them, exactly one has the reference
        # with source identifier 1-will-not-change and is unchanged
        if "unchanged" in event_types_2:
            assert (
                len(
                    [
                        reference_event
                        for reference_event in json_response["harvestings"][0][
                            "reference_events"
                        ]
                        if reference_event["reference"]["source_identifier"]
                        == "1-will-not-change"
                        and reference_event["type"] == "unchanged"
                    ]
                )
                == 1
            )
        # among them, exactly one has the reference
        # with source identifier 4-will-appear and is created
        if "created" in event_types_2:
            assert (
                len(
                    [
                        reference_event
                        for reference_event in json_response["harvestings"][0][
                            "reference_events"
                        ]
                        if reference_event["reference"]["source_identifier"]
                        == "4-will-appear"
                        and reference_event["type"] == "created"
                    ]
                )
                == 1
            )
        # among them, exactly one has the reference
        # with source identifier 3-will-disappear and is deleted
        if "deleted" in event_types_2:
            assert (
                len(
                    [
                        reference_event
                        for reference_event in json_response["harvestings"][0][
                            "reference_events"
                        ]
                        if reference_event["reference"]["source_identifier"]
                        == "3-will-disappear"
                        and reference_event["type"] == "deleted"
                    ]
                )
                == 1
            )
        # among them, exactly one has the reference
        # with source identifier 2-will-change and is updated
        if "updated" in event_types_2:
            assert (
                len(
                    [
                        reference_event
                        for reference_event in json_response["harvestings"][0][
                            "reference_events"
                        ]
                        if reference_event["reference"]["source_identifier"]
                        == "2-will-change"
                        and reference_event["type"] == "updated"
                    ]
                )
                == 1
            )
