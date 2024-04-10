import pytest
from semver import VersionInfo

from app.harvesters.hal.hal_references_converter import HalReferencesConverter
from app.harvesters.json_harvester_raw_result import JsonHarvesterRawResult

from app.harvesters.open_alex.open_alex_references_converter import (
    OpenAlexReferencesConverter,
)
from app.harvesters.scanr.scanr_references_converter import ScanrReferencesConverter
from app.services.hash.hash_service import HashService


@pytest.mark.asyncio
async def test_json_open_alex_hash(
    open_alex_api_work_to_hash: dict, open_alex_api_work_to_hash_2: dict
):
    """
    Test the JsonHash with OpenAlex documents
    when the raw data is the same but in different order
    """
    harvester_version = VersionInfo.parse("0.0.0")
    raw_data_1 = JsonHarvesterRawResult(
        source_identifier=open_alex_api_work_to_hash["id"],
        payload=open_alex_api_work_to_hash,
        formatter_name="OPEN_ALEX",
    )
    raw_data_2 = JsonHarvesterRawResult(
        source_identifier=open_alex_api_work_to_hash_2["id"],
        payload=open_alex_api_work_to_hash_2,
        formatter_name="OPEN_ALEX",
    )
    hash_service = HashService()
    hash_1 = hash_service.hash(
        raw_data=raw_data_1,
        hash_dict=OpenAlexReferencesConverter().hash_keys(
            harvester_version=harvester_version
        ),
    )
    hash_2 = hash_service.hash(
        raw_data=raw_data_2,
        hash_dict=OpenAlexReferencesConverter().hash_keys(
            harvester_version=harvester_version
        ),
    )

    assert hash_1 == hash_2


@pytest.mark.asyncio
async def test_json_hal_hash(
    hal_api_doc_for_hash_1: dict, hal_api_doc_for_hash_2: dict
):
    """
    Test the JsonHash with HAL documents
    when the raw data is the same but in different order
    """
    harvester_version = VersionInfo.parse("0.0.0")
    raw_data_1 = JsonHarvesterRawResult(
        source_identifier=hal_api_doc_for_hash_1["docid"],
        payload=hal_api_doc_for_hash_1,
        formatter_name="HAL",
    )
    raw_data_2 = JsonHarvesterRawResult(
        source_identifier=hal_api_doc_for_hash_2["docid"],
        payload=hal_api_doc_for_hash_2,
        formatter_name="HAL",
    )
    hash_service = HashService()

    hash_1 = hash_service.hash(
        raw_data_1,
        hash_dict=HalReferencesConverter().hash_keys(
            harvester_version=harvester_version
        ),
    )
    hash_2 = hash_service.hash(
        raw_data_2,
        hash_dict=HalReferencesConverter().hash_keys(
            harvester_version=harvester_version
        ),
    )

    assert hash_1 == hash_2


@pytest.mark.asyncio
async def test_json_scanr_hash(scanr_api_doc_hash_1: dict, scanr_api_doc_hash_2: dict):
    """
    Test the JsonHash with SCANR documents
    raw data is the same but in different order
    """
    harvester_version = VersionInfo.parse("0.0.0")
    raw_data_1 = JsonHarvesterRawResult(
        source_identifier=scanr_api_doc_hash_1["id"],
        payload=scanr_api_doc_hash_1,
        formatter_name="SCANR",
    )
    raw_data_2 = JsonHarvesterRawResult(
        source_identifier=scanr_api_doc_hash_2["id"],
        payload=scanr_api_doc_hash_2,
        formatter_name="SCANR",
    )
    hash_service = HashService()
    hash_1 = hash_service.hash(
        raw_data=raw_data_1,
        hash_dict=ScanrReferencesConverter().hash_keys(
            harvester_version=harvester_version
        ),
    )
    hash_2 = hash_service.hash(
        raw_data=raw_data_2,
        hash_dict=ScanrReferencesConverter().hash_keys(
            harvester_version=harvester_version
        ),
    )

    assert hash_1 == hash_2


@pytest.mark.asyncio
async def test_json_same_document(open_alex_api_work: dict):
    """
    Test the JsonHash with OpenAlex documents
    when the raw data is the same
    """
    harvester_version = VersionInfo.parse("0.0.0")
    raw_data = JsonHarvesterRawResult(
        source_identifier=open_alex_api_work["id"],
        payload=open_alex_api_work,
        formatter_name="OPEN_ALEX",
    )
    hash_service = HashService()
    hash_1 = hash_service.hash(
        raw_data=raw_data,
        hash_dict=OpenAlexReferencesConverter().hash_keys(
            harvester_version=harvester_version
        ),
    )
    hash_2 = hash_service.hash(
        raw_data=raw_data,
        hash_dict=OpenAlexReferencesConverter().hash_keys(
            harvester_version=harvester_version
        ),
    )

    assert hash_1 == hash_2
