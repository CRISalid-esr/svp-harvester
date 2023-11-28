from unittest import mock

import pytest
from fastapi.testclient import TestClient

from app.harvesters.scanr.scanr_harvester import ScanrHarvester
from app.harvesters.scanr.scanr_references_converter import ScanrReferencesConverter
from app.harvesters.scanr.scanr_elastic_client import ScanRElasticClient
from app.models.people import Person

REFERENCES_RETRIEVAL_API_PATH = "/api/v1/references/retrieval"


class MockScanRElasticClient(ScanRElasticClient):
    """
    Mock the elastic Client from Scanr harvester
    """
    mock_response = None

    def __init__(self):
        self.query = None

    async def perform_search(self, selected_index: ScanRElasticClient.Indexes):
        assert selected_index in self.Indexes, "Selected index is unavailable"

        resp = self.mock_response

        cleaned_results = self._clean_results(resp)

        for result in cleaned_results:
            yield result

    async def close(self):
        pass


def test_scanr_harvester_relevant_with_idref(person_with_name_and_idref: Person):
    """Test that the harvester will run if submitted with an IDREF."""
    harvester = ScanrHarvester(converter=ScanrReferencesConverter())
    assert harvester.is_relevant(person_with_name_and_idref) is True


def test_scanr_harvester_not_relevant_without_idref(person_with_name_and_orcid: Person):
    """Test that the harvester will not run if not submitted with an IDREF"""
    harvester = ScanrHarvester(converter=ScanrReferencesConverter())
    assert harvester.is_relevant(person_with_name_and_orcid) is False


@pytest.mark.asyncio
async def test_fetch_references_async(
        test_client: TestClient,
        person_with_name_and_idref_json,
        scanr_api_docs_from_publication,
):
    """
    Test a post request with history safe mode set to False.
    """
    MockScanRElasticClient.mock_response = scanr_api_docs_from_publication

    with mock.patch('app.harvesters.scanr.scanr_harvester.ScanRElasticClient',
                    new=MockScanRElasticClient):

        response = test_client.post(
            REFERENCES_RETRIEVAL_API_PATH,
            json={
                "person": person_with_name_and_idref_json,
                "events": ["created", "updated", "deleted", "unchanged"],
                "history_safe_mode": False,
                "harvesters": ["scanr"],
            }
        )

        assert response.status_code == 200
        json_response = response.json()
        retrieval_url = json_response["retrieval_url"]
        assert retrieval_url is not None

        response = test_client.get(retrieval_url)
        assert response.status_code == 200
        json_response = response.json()
        assert json_response["harvestings"][0]["harvester"] == "scanr"
        assert json_response["harvestings"][0]["state"] == "completed"
        assert len(json_response["harvestings"][0]["reference_events"]) == 1

        assert all(
            reference_event["type"] == "created"
            for reference_event in json_response["harvestings"][0]["reference_events"]
        )
