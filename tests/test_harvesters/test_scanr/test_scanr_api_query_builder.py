import pytest

from app.harvesters.scanr.scanr_api_query_builder import ScanRApiQueryBuilder


@pytest.fixture(name="scanr_query_builder")
def fixture_scanr_api_query_builder():
    """Fixture for ScanRApiQueryBuilder instance"""
    scanr_query = ScanRApiQueryBuilder()

    yield scanr_query


def test_set_query(scanr_query_builder):
    """Test if the set_query function return the values set"""
    scanr_query_builder.set_publication_query("idref09850")

    assert scanr_query_builder.scanr_id == "idref09850"


def test_build_person_query_with_idref(scanr_query_builder):
    """
    GIVEN a ScanRApiQueryBuilder instance
    WHEN the build function is called with the identifier type set on AUTH_IDREF
    THEN the query contains a filter with the "id" parameter

    :param scanr_query_builder:
    :return:
    """
    scanr_query_builder.set_person_query(
        scanr_query_builder.QueryParameters.AUTH_IDREF, "idref2556"
    )
    query = scanr_query_builder.build()

    expected_result = {
        "_source": ["id", "externalIds", "domains", "affiliations", "fullName"],
        "query": {
            "bool": {
                "must": [
                    {"term": {"externalIds.type.keyword": "idref"}},
                    {"term": {"externalIds.id.keyword": "idref2556"}},
                ]
            }
        },
    }
    assert query == expected_result


def test_build_person_query_with_orcid(scanr_query_builder):
    """
    GIVEN a ScanRApiQueryBuilder instance
    WHEN the build function is called with the identifier type set on AUTH_ORCID
    THEN the query contains a filter with the "orcid" parameter

    :param scanr_query_builder:
    :return:
    """
    scanr_query_builder.set_person_query(
        scanr_query_builder.QueryParameters.AUTH_ORCID, "idref2556"
    )
    query = scanr_query_builder.build()

    expected_result = {
        "_source": ["id", "externalIds", "domains", "affiliations", "fullName"],
        "query": {
            "bool": {
                "must": [
                    {"term": {"externalIds.type.keyword": "orcid"}},
                    {"term": {"externalIds.id.keyword": "idref2556"}},
                ]
            }
        },
    }
    assert query == expected_result


def test_build_person_query_without_idref_or_orcid(scanr_query_builder):
    """
    GIVEN a ScanRApiQueryBuilder instance
    WHEN the build function is called with the identifier type
    not set on AUTH_IDREF or AUTH_ORCID
    THEN the query contains a filter with the "externalIds.type.keyword"
    and "externalIds.id.keyword" parameters

    :param scanr_query_builder:
    :return:
    """
    scanr_query_builder.set_person_query(
        scanr_query_builder.QueryParameters.AUTH_ID_HAL_S, "john-doe"
    )
    query = scanr_query_builder.build()

    expected_result = {
        "_source": ["id", "externalIds", "domains", "affiliations", "fullName"],
        "query": {
            "bool": {
                "must": [
                    {"term": {"externalIds.type.keyword": "id_hal"}},
                    {"term": {"externalIds.id.keyword": "john-doe"}},
                ]
            }
        },
    }
    assert query == expected_result


def test_build_publication_query_with_idref(scanr_query_builder):
    """
    GIVEN a ScanRApiQueryBuilder instance
    WHEN the build function is called with the identifier type set to AUTH_IDREF
    THEN the query contains a filter with the "authors.person" parameter

    :param scanr_query_builder:
    :return:
    """
    scanr_query_builder.set_publication_query("idref2556")
    query = scanr_query_builder.build()

    expected_result = {
        "_source": [
            "id",
            "title",
            "summary",
            "type",
            "productionType",
            "publicationDate",
            "domains",
            "affiliations",
            "authors",
            "externalIds",
        ],
        "query": {"bool": {"must": [{"term": {"authors.person": "idref2556"}}]}},
        "sort": {"publicationDate": {"order": "desc"}},
    }

    assert query == expected_result
