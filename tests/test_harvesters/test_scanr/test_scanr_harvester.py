from unittest import mock
from elasticsearch import AsyncElasticsearch
import pytest
from fastapi.testclient import TestClient

from app.harvesters.scanr.scanr_harvester import ScanrHarvester
from app.harvesters.scanr.scanr_references_converter import ScanrReferencesConverter
from app.models.people import Person

REFERENCES_RETRIEVAL_API_PATH = "/api/v1/references/retrieval"


def test_scanr_harvester_relevant_with_idref(person_with_name_and_idref: Person):
    """Test that the harvester will run if submitted with an IDREF."""
    harvester = ScanrHarvester(converter=ScanrReferencesConverter())
    assert harvester.is_relevant(person_with_name_and_idref) is True


def test_scanr_harvester_relevant_with_orcid(person_with_name_and_orcid: Person):
    """Test that the harvester will not run if not submitted with an IDREF"""
    harvester = ScanrHarvester(converter=ScanrReferencesConverter())
    assert harvester.is_relevant(person_with_name_and_orcid) is True


def test_scanr_harvester_not_relevant_with_halid_s(
    person_with_name_and_id_hal_s: Person,
):
    """Test that the harvester will not run if not submitted with an IDREF"""
    harvester = ScanrHarvester(converter=ScanrReferencesConverter())
    assert harvester.is_relevant(person_with_name_and_id_hal_s) is True


def test_scanr_harvester_not_relevant_with_person_without_identifiers(
    person_without_identifiers: Person,
):
    """Test that the harvester will not run if not submitted with an IDREF"""
    harvester = ScanrHarvester(converter=ScanrReferencesConverter())
    assert harvester.is_relevant(person_without_identifiers) is False


@pytest.mark.asyncio
async def test_fetch_references_async_with_idref(
    test_client: TestClient,
    person_with_name_and_idref_json,
    scanr_api_docs_from_publication,
):
    """
    Test a post request with history safe mode set to False and a person with an IDREF
    """

    with mock.patch.object(
        AsyncElasticsearch,
        "search",
        new=mock.AsyncMock(return_value=scanr_api_docs_from_publication),
    ):
        response = test_client.post(
            REFERENCES_RETRIEVAL_API_PATH,
            json={
                "person": person_with_name_and_idref_json,
                "events": ["created", "updated", "deleted", "unchanged"],
                "harvesters": ["scanr"],
            },
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


@pytest.mark.asyncio
async def test_fetch_references_async_with_orcid(
    test_client: TestClient,
    person_with_name_and_orcid_json,
    scanr_api_docs_from_publication,
):
    """
    Test a post request with history safe mode set to False and with an ORCID.
    """

    with mock.patch.object(
        AsyncElasticsearch,
        "search",
        new=mock.AsyncMock(return_value=scanr_api_docs_from_publication),
    ), mock.patch.object(
        ScanrHarvester,
        "_get_entity_scanr_id",
        new=mock.AsyncMock(return_value="idref123456789"),
    ):
        response = test_client.post(
            REFERENCES_RETRIEVAL_API_PATH,
            json={
                "person": person_with_name_and_orcid_json,
                "events": ["created", "updated", "deleted", "unchanged"],
                "harvesters": ["scanr"],
            },
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
