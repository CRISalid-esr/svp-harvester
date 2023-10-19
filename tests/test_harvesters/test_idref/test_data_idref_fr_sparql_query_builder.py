""" Test for the hal api query builder"""

import pytest

from app.harvesters.idref.idref_sparql_query_builder import IdrefSparqlQueryBuilder


def test_build_query_without_subject_type_raises_error():
    """
    GIVEN a HalApiQueryBuilder instance
    WHEN the subject type is not set
    THEN an AssertionError is raised

    :return: None
    """
    idref_query_builder = IdrefSparqlQueryBuilder()
    with pytest.raises(AssertionError):
        idref_query_builder.build()

def test_build_query_for_person_with_idref():
    """
    GIVEN a HalApiQueryBuilder instance
    WHEN the idref parameter is set
    THEN the query filter is in the query

    :return: None
    """
    idref_query_builder = IdrefSparqlQueryBuilder()
    idref_query_builder.set_subject_type(IdrefSparqlQueryBuilder.SubjectType.PERSON)
    idref_id = "test_idref_id"
    idref_query_builder.set_idref_id(idref_id)
    assert idref_query_builder.subject_uri == f"http://www.idref.fr/{idref_id}/id"
    query = idref_query_builder.build()
    assert f"?pub ?role <http://www.idref.fr/{idref_id}/id> ." in query


def test_build_query_for_person_with_orcid():
    """
    GIVEN a HalApiQueryBuilder instance
    WHEN the orcid parameter is set
    THEN the query filter is in the query

    :return: None
    """
    idref_query_builder = IdrefSparqlQueryBuilder()
    idref_query_builder.set_subject_type(IdrefSparqlQueryBuilder.SubjectType.PERSON)
    orcid = "test_orcid"
    idref_query_builder.set_orcid(orcid)
    query = idref_query_builder.build()
    assert "?pub ?role ?pers ." in query
    assert f"?pers vivo:orcidId \"{orcid}\" ." in query
