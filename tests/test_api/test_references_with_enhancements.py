"""Test that references API creates Retrieval in database."""

from unittest import mock

import aiohttp
import pytest
from fastapi.testclient import TestClient
from semver import VersionInfo

import app.harvesters.hal.hal_harvester

pytestmark = pytest.mark.integration

REFERENCES_RETRIEVAL_API_PATH = "/api/v1/references/retrieval"


@pytest.mark.asyncio
async def test_fetch_unchanged_references_async_with_enhancements_returned(  # pylint: disable=too-many-statements
    test_client: TestClient,
    person_with_name_and_id_hal_i_json,
    hal_api_docs_for_researcher_version_1,
):
    """
    Test two posts with unchanged version and the results
    but the harvester has been enhanced between the two requests
    and fetch_enhancements is set to True
    We don't ask for unchanged events but they are generated
    as the harvester has been enhanced

    :param test_client:
    :param person_with_name_and_id_hal_i_json:
    :param hal_api_docs_for_researcher_version_1:
    :return:
    """
    # 1. First launch a retrieval that will create 3 references in the database
    with mock.patch.object(aiohttp.ClientSession, "get") as aiohttp_client_session_get:
        aiohttp_client_session_get.return_value.__aenter__.return_value.status = 200
        aiohttp_client_session_get.return_value.__aenter__.return_value.json.return_value = (
            hal_api_docs_for_researcher_version_1
        )

        response = test_client.post(
            REFERENCES_RETRIEVAL_API_PATH,
            json={
                "person": person_with_name_and_id_hal_i_json,
                "events": ["created", "updated", "deleted"],
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
        # 2. Now increase the version of the harvester
        # and launch a new retrieval with the same person and events
        # It will return the same results as the previous one
        # but with the "enhanced" flag set to True
        # Unchanged events are generated althoug we don't ask for them
        with mock.patch.object(
            app.harvesters.hal.hal_harvester.HalHarvester, "get_version"
        ) as hal_harvester_version:
            # ensure this is always a higher version than the real one
            hal_harvester_version.return_value = VersionInfo.parse("99.0.0")
            response = test_client.post(
                REFERENCES_RETRIEVAL_API_PATH,
                json={
                    "person": person_with_name_and_id_hal_i_json,
                    "events": ["created", "updated", "deleted"],
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
            # assert that all 3 references are returned with "enhanced" flag set to true
            assert len(json_response["harvestings"][0]["reference_events"]) == 3
            assert all(
                reference_event["type"] == "unchanged"
                for reference_event in json_response["harvestings"][0][
                    "reference_events"
                ]
            )
            assert all(
                reference_event["enhanced"]
                for reference_event in json_response["harvestings"][0][
                    "reference_events"
                ]
            )


@pytest.mark.asyncio
async def test_fetch_unchanged_references_async_with_enhancements_not_returned(  # pylint: disable=too-many-statements
    test_client: TestClient,
    person_with_name_and_id_hal_i_json,
    hal_api_docs_for_researcher_version_1,
):
    """
    Test two posts with unchanged version and the results.
    The harvester has been enhanced between the two requests
    and fetch_enhancements is set to False
    As we don't ask for enhancements nor for unchanged events,
    no reference is returned

    :param test_client:
    :param person_with_name_and_id_hal_i_json:
    :param hal_api_docs_for_researcher_version_1:
    :return:
    """
    # 1. First launch a retrieval that will create 3 references in the database
    with mock.patch.object(aiohttp.ClientSession, "get") as aiohttp_client_session_get:
        aiohttp_client_session_get.return_value.__aenter__.return_value.status = 200
        aiohttp_client_session_get.return_value.__aenter__.return_value.json.return_value = (
            hal_api_docs_for_researcher_version_1
        )

        response = test_client.post(
            REFERENCES_RETRIEVAL_API_PATH,
            json={
                "person": person_with_name_and_id_hal_i_json,
                "events": ["created", "updated", "deleted"],
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
        # 2. Now increase the version of the harvester
        # and launch a new retrieval with the same person and events
        # It will not return any reference as we don't ask for enhancements
        with mock.patch.object(
            app.harvesters.hal.hal_harvester.HalHarvester, "get_version"
        ) as hal_harvester_version:
            # ensure this is always a higher version than the real one
            hal_harvester_version.return_value = VersionInfo.parse("99.0.0")
            response = test_client.post(
                REFERENCES_RETRIEVAL_API_PATH,
                json={
                    "person": person_with_name_and_id_hal_i_json,
                    "events": ["created", "updated", "deleted"],
                    "fetch_enhancements": False,
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
            # assert that no reference is returned
            assert len(json_response["harvestings"][0]["reference_events"]) == 0


@pytest.mark.asyncio
async def test_fetch_modified_references_async_with_enhancements_returned(  # pylint: disable=too-many-statements
    test_client: TestClient,
    person_with_name_and_id_hal_i_json,
    hal_api_docs_for_researcher_version_1,
    hal_api_docs_for_researcher_version_2,
):
    """
    Test two posts with changed version and the results.
    The harvester has been enhanced between the two requests
    and fetch_enhancements is set to True
    We will get unchanged, updated, deleted and created events
    and updated/unchanged events will have the "enhanced" flag set to True

    :param test_client:
    :param person_with_name_and_id_hal_i_json:
    :param hal_api_docs_for_researcher_version_1:
    :param hal_api_docs_for_researcher_version_2:
    :return:
    """
    # 1. First launch a retrieval that will create 3 references in the database
    with mock.patch.object(aiohttp.ClientSession, "get") as aiohttp_client_session_get:
        aiohttp_client_session_get.return_value.__aenter__.return_value.status = 200
        aiohttp_client_session_get.return_value.__aenter__.return_value.json.return_value = (
            hal_api_docs_for_researcher_version_1
        )

        response = test_client.post(
            REFERENCES_RETRIEVAL_API_PATH,
            json={
                "person": person_with_name_and_id_hal_i_json,
                "events": ["created", "updated", "deleted"],
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
        # 2. Now increase the version of the harvester
        # and launch a new retrieval with the same person and events
        # It will return changed results
        # reference with source_identifier "1-will-not-change" will be unchanged but enhanced
        # reference with source_identifier "2-will-change" will be updated and enhanced
        # reference with source_identifier "3-will-disappear" will be marked as deleted (not enhanced)
        # reference with source_identifier "4-will-appear" will be marked as created (not enhanced)
    with mock.patch.object(aiohttp.ClientSession, "get") as aiohttp_client_session_get:
        aiohttp_client_session_get.return_value.__aenter__.return_value.status = 200
        aiohttp_client_session_get.return_value.__aenter__.return_value.json.return_value = (
            hal_api_docs_for_researcher_version_2
        )
        with mock.patch.object(
            app.harvesters.hal.hal_harvester.HalHarvester, "get_version"
        ) as hal_harvester_version:
            # ensure this is always a higher version than the real one
            hal_harvester_version.return_value = VersionInfo.parse("99.0.0")
            response = test_client.post(
                REFERENCES_RETRIEVAL_API_PATH,
                json={
                    "person": person_with_name_and_id_hal_i_json,
                    "events": ["created", "updated", "deleted"],
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
            # assert that the reference with source_identifier "1-will-not-change"
            # is returned as unchanged with "enhanced" flag set to true
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
                        and reference_event["enhanced"]
                    ]
                )
                == 1
            )
            # assert that the reference with source_identifier "2-will-change"
            # is returned as updated with "enhanced" flag set to true
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
                        and reference_event["enhanced"]
                    ]
                )
                == 1
            )
            # assert that the reference with source_identifier "3-will-disappear"
            # is returned as deleted with "enhanced" flag set to false
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
                        and not reference_event["enhanced"]
                    ]
                )
                == 1
            )
            # assert that the reference with source_identifier "4-will-appear"
            # is returned as created with "enhanced" flag set to false
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
                        and not reference_event["enhanced"]
                    ]
                )
                == 1
            )
