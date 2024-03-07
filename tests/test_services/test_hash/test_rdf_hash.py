import pytest
from app.harvesters.idref.persee_references_converter import PerseeReferencesConverter
from app.harvesters.idref.science_plus_references_converter import (
    SciencePlusReferencesConverter,
)
from app.harvesters.idref.sudoc_references_converter import SudocReferencesConverter
from app.harvesters.rdf_harvester_raw_result import RdfHarvesterRawResult
from app.services.hash.hash_service import HashService


@pytest.mark.asyncio
async def test_rdf_sudoc_hash(sudoc_rdf_graph_for_hash_1, sudoc_rdf_graph_for_hash_2):
    """
    Test the RdfHash with Sudoc documents
    when the raw data is the same but in different order
    """
    raw_data_1 = RdfHarvesterRawResult(
        source_identifier="http://www.sudoc.fr/193726130/id",
        payload=sudoc_rdf_graph_for_hash_1,
        formatter_name="Sudoc",
    )
    raw_data_2 = RdfHarvesterRawResult(
        source_identifier="http://www.sudoc.fr/193726130/id",
        payload=sudoc_rdf_graph_for_hash_2,
        formatter_name="Sudoc",
    )

    hash_service = HashService()
    hash_1 = hash_service.hash(
        raw_data=raw_data_1, hash_dict=SudocReferencesConverter().hash_keys()
    )
    hash_2 = hash_service.hash(
        raw_data=raw_data_2, hash_dict=SudocReferencesConverter().hash_keys()
    )

    assert hash_1 == hash_2


@pytest.mark.asyncio
async def test_rdf_science_plus_hash(
    science_plus_rdf_graph_for_hash_1, science_plus_rdf_graph_for_hash_2
):
    """
    Test the RdfHash with Science Plus documents
    when the raw data is the same but in different order
    """
    raw_data_1 = RdfHarvesterRawResult(
        source_identifier="http://hub.abes.fr/cairn/periodical/autr/2008/issue_autr045/D33AF39D3B7834E0E053120B220A2036/w",
        payload=science_plus_rdf_graph_for_hash_1,
        formatter_name="Science Plus",
    )
    raw_data_2 = RdfHarvesterRawResult(
        source_identifier="http://hub.abes.fr/cairn/periodical/autr/2008/issue_autr045/D33AF39D3B7834E0E053120B220A2036/w",
        payload=science_plus_rdf_graph_for_hash_2,
        formatter_name="Science Plus",
    )

    hash_service = HashService()
    hash_1 = hash_service.hash(
        raw_data=raw_data_1, hash_dict=SciencePlusReferencesConverter().hash_keys()
    )
    hash_2 = hash_service.hash(
        raw_data=raw_data_2, hash_dict=SciencePlusReferencesConverter().hash_keys()
    )

    assert hash_1 == hash_2


@pytest.mark.asyncio
async def test_rdf_persee_hash(persee_rdf_xml_for_hash_1, persee_rdf_xml_for_hash_2):
    """
    Test the RdfHash with Persee documents
    when the raw data is the same but in different order
    """
    raw_data_1 = RdfHarvesterRawResult(
        source_identifier="http://data.persee.fr/doc/hista_0992-2059_1998_num_42_1_2826#Web",
        payload=persee_rdf_xml_for_hash_1,
        formatter_name="Persee",
    )
    raw_data_2 = RdfHarvesterRawResult(
        source_identifier="http://data.persee.fr/doc/hista_0992-2059_1998_num_42_1_2826#Web",
        payload=persee_rdf_xml_for_hash_2,
        formatter_name="Persee",
    )

    hash_service = HashService()
    hash_1 = hash_service.hash(
        raw_data=raw_data_1, hash_dict=PerseeReferencesConverter().hash_keys()
    )
    hash_2 = hash_service.hash(
        raw_data=raw_data_2, hash_dict=PerseeReferencesConverter().hash_keys()
    )

    assert hash_1 == hash_2
