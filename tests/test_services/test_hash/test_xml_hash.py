from loguru import logger
import pytest
from app.harvesters.idref.open_edition_references_converter import (
    OpenEditionReferencesConverter,
)

from app.harvesters.xml_harvester_raw_result import XMLHarvesterRawResult
from app.services.hash.hash_service import HashService


@pytest.mark.asyncio
async def test_xml_open_edition_hash(
    open_edition_xml_for_hash_1, open_edition_xml_for_hash_2
):
    """
    Test the XMLHash with Open Edition documents
    when the raw data is the same but in different order
    """
    raw_data_1 = XMLHarvesterRawResult(
        source_identifier="https://journals.openedition.org/conflits/basictei/756",
        payload=open_edition_xml_for_hash_1,
        formatter_name="OPEN_EDITION",
    )
    raw_data_2 = XMLHarvesterRawResult(
        source_identifier="https://journals.openedition.org/conflits/basictei/756",
        payload=open_edition_xml_for_hash_2,
        formatter_name="OPEN_EDITION",
    )

    hash_service = HashService()
    hash_1 = hash_service.hash(
        raw_data=raw_data_1, hash_dict=OpenEditionReferencesConverter().hash_keys()
    )
    hash_2 = hash_service.hash(
        raw_data=raw_data_2, hash_dict=OpenEditionReferencesConverter().hash_keys()
    )

    logger.info(f"hash_1: {hash_1}")
    logger.info(f"hash_2: {hash_2}")
    assert hash_1 == hash_2


@pytest.mark.asyncio
async def test_xml_hash(open_edition_xml_for_hash_1):
    """
    Test the XMLHash with Open Edition documents
    when the raw data is the same
    """
    raw_data = XMLHarvesterRawResult(
        source_identifier="https://journals.openedition.org/conflits/basictei/756",
        payload=open_edition_xml_for_hash_1,
        formatter_name="OPEN_EDITION",
    )

    hash_service = HashService()
    hash_1 = hash_service.hash(
        raw_data=raw_data, hash_dict=OpenEditionReferencesConverter().hash_keys()
    )
    hash_2 = hash_service.hash(
        raw_data=raw_data, hash_dict=OpenEditionReferencesConverter().hash_keys()
    )
    assert hash_1 == hash_2
