""" Test for the hal api query builder"""
from urllib.parse import parse_qs

import pytest

from app.harvesters.hal.hal_api_query_builder import HalApiQueryBuilder


@pytest.fixture(name="hal_query_builder")
def fixture_hal_api_query_builder():
    """fixture for HalApiQueryBuilder instance"""
    hal_query = HalApiQueryBuilder()

    hal_query.fields = ["field1", "field2", "field3"]  # Set fields in fixture
    hal_query.doc_types = ["ART", "OUV", "COUV"]  # Set doc_types in fixture
    hal_query.sort_parameter = "test_key_parameter"  # Set sort_parameter in fixture
    hal_query.sort_direction = "dsc"  # Set sort_direction in fixture

    yield hal_query  # yield is used here instead of return for future flexibility


def test_set_query(hal_query_builder):
    """Test if the set_query function return the values set"""
    hal_query_builder.set_query(
        hal_query_builder.QueryParameters.AUTH_ID_HAL_I, "test_value"
    )

    assert hal_query_builder.identifier_type.value == "authIdHal_i"
    assert hal_query_builder.identifier_value == "test_value"


def test_build_query_with_idhal_i(hal_query_builder):
    """
    GIVEN a HalApiQueryBuilder instance
    WHEN the build function is called with the identifier type set to AUTH_ID_HAL_I
    THEN the query contains a filter with the authIdHal_i parameter

    :param hal_query_builder:
    :return:
    """

    test_idhal_i = "123456"

    hal_query_builder.set_query(
        hal_query_builder.QueryParameters.AUTH_ID_HAL_I, test_idhal_i
    )

    result = hal_query_builder.build()
    result_dict = parse_qs(result)

    expected_result = {
        "fl": ["field1,field2,field3"],
        "fq": ["docType_s:(ART OR OUV OR COUV)"],
        "q": [f"authIdHal_i:{test_idhal_i}"],
        "rows": ["1000"],
        "sort": ["test_key_parameter dsc"],
    }

    assert result_dict == expected_result


def test_build_query_with_orcid_id(hal_query_builder):
    """
    GIVEN a HalApiQueryBuilder instance
    WHEN the build function is called with the identifier type set to AUTH_ORCID_ID_EXT_ID
    THEN the query contains a filter with the authORCIDIdExt_id parameter surrounded by quotes

    :param hal_query_builder:
    :return:
    """
    orcid = "0000-0002-1825-0097"
    hal_query_builder.set_query(
        hal_query_builder.QueryParameters.AUTH_ORCID_ID_EXT_ID, orcid
    )

    result = hal_query_builder.build()
    result_dict = parse_qs(result)

    expected_result = {
        "fl": ["field1,field2,field3"],
        "fq": ["docType_s:(ART OR OUV OR COUV)"],
        "q": [f'authORCIDIdExt_id:"{orcid}"'],
        "rows": ["1000"],
        "sort": ["test_key_parameter dsc"],
    }

    assert result_dict == expected_result


def test_build_query_with_invalid_identifier_type(hal_query_builder):
    """Test if the set_query function raise an error if the identifier type is not valid"""
    with pytest.raises(TypeError):
        hal_query_builder.set_query("foobar", "test_value")


def test_build_query__without_identifier_value_set(hal_query_builder):
    """Test if the build function raise an error if the value of the identifier is not set"""
    hal_query_builder.set_query(hal_query_builder.QueryParameters.AUTH_ID_HAL_I, None)

    with pytest.raises(AssertionError):
        hal_query_builder.build()


def test_build_query__without_set_query_set(hal_query_builder):
    """Test if the build function raise an error if the set_query is not set"""
    with pytest.raises(AssertionError):
        hal_query_builder.build()
