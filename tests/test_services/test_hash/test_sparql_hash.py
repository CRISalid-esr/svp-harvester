import pytest
from app.harvesters.idref.idref_basic_references_converter import (
    IdrefBasicReferencesConverter,
)

from app.harvesters.sparql_harvester_raw_result import SparqlHarvesterRawResult
from app.services.hash.hash_service import HashService


@pytest.mark.asyncio
async def test_sparql_idref_hash(idref_pub_converted_1, idref_pub_converted_2):
    """
    Test the SparqlHash with Idref documents
    when the raw data is the same but in different order
    """
    raw_data_1 = SparqlHarvesterRawResult(
        source_identifier=idref_pub_converted_1["uri"],
        payload=idref_pub_converted_1,
        formatter_name="Idref",
    )

    raw_data_2 = SparqlHarvesterRawResult(
        source_identifier=idref_pub_converted_2["uri"],
        payload=idref_pub_converted_2,
        formatter_name="Idref",
    )

    hash_service = HashService()
    hash_1 = hash_service.hash(
        raw_data=raw_data_1, hash_dict=IdrefBasicReferencesConverter().hash_keys()
    )
    hash_2 = hash_service.hash(
        raw_data=raw_data_2, hash_dict=IdrefBasicReferencesConverter().hash_keys()
    )

    assert hash_1 == hash_2
