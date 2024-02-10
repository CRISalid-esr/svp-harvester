"""Test that references API creates Retrieval in database."""
from unittest import mock

import aiohttp
import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration

REFERENCES_RETRIEVAL_API_PATH = "/api/v1/references/retrieval"


@pytest.mark.asyncio
@pytest.mark.current
async def test_fetch_references_contributions_history(  # pylint: disable=too-many-statements, too-many-locals
    test_client: TestClient,
    person_with_name_and_id_hal_i_json,
    hal_api_docs_with_inconsistent_contributors,
):
    """
    Test that a hal api response where a contributors is mentioned twice
    with the same identifier but different names is handled correctly


    :param test_client:
    :param person_with_name_and_id_hal_i_json:
    :param hal_api_docs_with_inconsistent_contributors:
    :return:
    """
    # First request, will fetch the first version of the bibliographic records
    with mock.patch.object(aiohttp.ClientSession, "get") as aiohttp_client_session_get:
        aiohttp_client_session_get.return_value.__aenter__.return_value.status = 200
        aiohttp_client_session_get.return_value.__aenter__.return_value.json.return_value = (
            hal_api_docs_with_inconsistent_contributors
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
        assert len(json_response["harvestings"][0]["reference_events"]) == 1
        events = json_response["harvestings"][0]["reference_events"]
        reference = _extract_reference_by_source_identifier(events, "halshs-02514028")
        assert reference is not None
        reference_contributions = reference["reference"]["contributions"]
        assert len(reference_contributions) == 17
        # one of the contributors has the source identifier '183355'
        # and its name may be 'Laïla Nehmé' or 'Laila Nehmé'
        assert any(
            c["contributor"]["source_identifier"] == "183355"
            and c["contributor"]["name"] in ["Laïla Nehmé", "Laila Nehmé"]
            for c in reference_contributions
        )


def _extract_reference_by_source_identifier(events, source_identifier):
    for event in events:
        if event["reference"]["source_identifier"] == source_identifier:
            return event
    return None


def _extract_contribution_by_rank(contributions, rank):
    return next(c for c in contributions if c["rank"] == rank)
