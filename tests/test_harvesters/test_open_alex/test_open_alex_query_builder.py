from urllib.parse import parse_qs
import pytest

from app.harvesters.open_alex.open_alex_api_query_builder import OpenAlexQueryBuilder


@pytest.fixture(name="open_alex_query_builder")
def fixture_hal_api_query_builder():
    """fixture for HalApiQueryBuilder instance"""
    open_alex_query = OpenAlexQueryBuilder()

    yield open_alex_query


def test_set_query(open_alex_query_builder):
    """Test if the set_query function return the values set"""
    open_alex_query_builder.set_query(
        open_alex_query_builder.QueryParameters.AUTH_ORCID, "test_value"
    )

    assert open_alex_query_builder.identifier_type.value == "orcid"
    assert open_alex_query_builder.identifier_value == "test_value"


def test_set_subject_type(open_alex_query_builder):
    """Test if the set_subject_type function return the values set"""
    open_alex_query_builder.set_subject_type(open_alex_query_builder.SubjectType.PERSON)

    assert open_alex_query_builder.subject_type.value == "author"


def test_build_query_without_subject_type(open_alex_query_builder):
    """
    GIVEN a OpenAlexQueryBuilder instance
    WHEN the build function is called without setting the subject type
    THEN raise an assertion error

    :param open_alex_query_builder:
    :return:
    """

    test_orcid = "0000-0002-1825-0097"

    open_alex_query_builder.set_query(
        open_alex_query_builder.QueryParameters.AUTH_ORCID, test_orcid
    )

    with pytest.raises(NotImplementedError):
        open_alex_query_builder.build()


def test_build_query_for_person_with_orcid(open_alex_query_builder):
    """
    GIVEN a OpenAlexQueryBuilder instance
    WHEN the build function is called with the identifier type set to AUTH_ORCID
    THEN the query contains a filter with the orcid parameter

    :param open_alex_query_builder:
    :return:
    """

    test_orcid = "0000-0002-1825-0097"

    open_alex_query_builder.set_query(
        open_alex_query_builder.QueryParameters.AUTH_ORCID, test_orcid
    )
    open_alex_query_builder.set_subject_type(open_alex_query_builder.SubjectType.PERSON)

    result = open_alex_query_builder.build()
    result_dict = parse_qs(result)

    expected_result = {
        "filter": [f"author.orcid:{test_orcid}"],
    }

    assert result_dict == expected_result


def test_build_query_with_indaliv_identifier_type(open_alex_query_builder):
    """Test if the set_query function raise an error if the identifier type is not valid"""

    test_indaliv = "123456"

    with pytest.raises(TypeError):
        open_alex_query_builder.set_query("foobar", test_indaliv)


def test_build_query_without_set_query(open_alex_query_builder):
    """Test if the build function raise an error if the query is not set"""
    with pytest.raises(AssertionError):
        open_alex_query_builder.build()
