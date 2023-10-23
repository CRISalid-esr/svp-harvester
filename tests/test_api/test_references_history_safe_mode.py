"""Test that references API creates Retrieval in database."""
from unittest import mock

import aiohttp
import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration

REFERENCES_RETRIEVAL_API_PATH = "/api/v1/references/retrieval"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "history_safe_mode",
    [True, False],
)
async def test_fetch_references_async_with_history_safe_or_unsafe(  # pylint: disable=too-many-statements
    test_client: TestClient,
    person_with_name_and_id_hal_i_json,
    hal_api_docs_for_researcher_version_1,
    hal_api_docs_for_researcher_version_2,
    history_safe_mode,
):
    """
    Test one post request with history safe mode set to False followed by two others,
    with history safe mode set to True or Flase by parametrization.
    The last two requests return an identical new version of the results.
    With history safe mode set to False, the last request only returns "unchanged" reference events.
    With history safe mode set to True, the last request returns all types of reference events.



    :param test_client:
    :param person_with_name_and_id_hal_i_json:
    :param hal_api_docs_for_researcher_version_1:
    :param hal_api_docs_for_researcher_version_2:
    :return:
    """
    # 1. First launch a retrieval with history safe mode set to False
    # that will create the 3 references in the database
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
                "history_safe_mode": False,
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
        assert len(json_response["harvestings"][0]["reference_events"]) == 3
        # all reference events are of type created
        assert all(
            reference_event["type"] == "created"
            for reference_event in json_response["harvestings"][0]["reference_events"]
        )
    # 2. Now relaunch the same retrieval
    # with history safe mode set to True or False by parametrization
    # It will return a new version of the results
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
                "history_safe_mode": history_safe_mode,
            },
        )
        assert response.status_code == 200
        json_response = response.json()
        retrieval_url = json_response["retrieval_url"]
        assert retrieval_url is not None
        # while state is not completed, continue querying
        response = test_client.get(retrieval_url)
        assert response.status_code == 200
        json_response = response.json()
        assert json_response["harvestings"][0]["state"] == "completed"
        # one and only one "deleted" event occured
        # only for reference with source identifier 3-will-disappear
        assert (
            len(
                [
                    reference_event
                    for reference_event in json_response["harvestings"][0][
                        "reference_events"
                    ]
                    if reference_event["type"] == "deleted"
                    and reference_event["reference"]["source_identifier"]
                    == "3-will-disappear"
                ]
            )
            == 1
        )
    # 3. Now launch the same request again, it will return the same results as the previous one
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
                "history_safe_mode": history_safe_mode,
            },
        )
        assert response.status_code == 200
        json_response = response.json()
        retrieval_url = json_response["retrieval_url"]
        assert retrieval_url is not None
        # while state is not completed, continue querying
        response = test_client.get(retrieval_url)
        assert response.status_code == 200
        json_response = response.json()
        assert json_response["harvestings"][0]["state"] == "completed"
        assert json_response["harvestings"][0]["harvester"] == "hal"
        # if history safe mode is False, all reference events are of type unchanged
        if not history_safe_mode:
            # there are 3 reference events
            assert len(json_response["harvestings"][0]["reference_events"]) == 3
            # all of type unchanged
            assert all(
                reference_event["type"] == "unchanged"
                for reference_event in json_response["harvestings"][0][
                    "reference_events"
                ]
            )
            # reference with source identifier 3-will-disappear does not appear in the results
            assert all(
                reference_event["reference"]["source_identifier"] != "3-will-disappear"
                for reference_event in json_response["harvestings"][0][
                    "reference_events"
                ]
            )
        if history_safe_mode:
            # there are 4 reference events
            assert len(json_response["harvestings"][0]["reference_events"]) == 4
            # if history safe mode is True, reference events are
            # of type created, updated, deleted or unchanged
            # reference by source identifier 1-will-not-change
            # is unchanged (reference events order is not guaranteed)
            assert any(
                reference_event["type"] == "unchanged"
                and reference_event["reference"]["source_identifier"]
                == "1-will-not-change"
                for reference_event in json_response["harvestings"][0][
                    "reference_events"
                ]
            )
            # reference by source identifier 4-will-appear is created
            assert any(
                reference_event["type"] == "created"
                and reference_event["reference"]["source_identifier"] == "4-will-appear"
                for reference_event in json_response["harvestings"][0][
                    "reference_events"
                ]
            )
            # reference by source identifier 3-will-disappear is deleted
            assert any(
                reference_event["type"] == "deleted"
                and reference_event["reference"]["source_identifier"]
                == "3-will-disappear"
                for reference_event in json_response["harvestings"][0][
                    "reference_events"
                ]
            )
            # reference by source identifier 2-will-change is updated
            assert any(
                reference_event["type"] == "updated"
                and reference_event["reference"]["source_identifier"] == "2-will-change"
                for reference_event in json_response["harvestings"][0][
                    "reference_events"
                ]
            )
