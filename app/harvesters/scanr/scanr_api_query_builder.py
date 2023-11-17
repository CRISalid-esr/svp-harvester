from enum import Enum

# TODO: Redo the builder. Create differents type of queries: person queries and publication queries.
#  1-For publication queries, if idref is given, => do the search.
#     If not, need to do a person query to get the id, and then be able to perform the publication query.
#  2-For person queries, if idref is given => concatenate idref + value of idref and search on "id" field.
#    If orcid given, search on "orcid" field.
#    Else search on "ExternalIds" field


class ScanRApiQueryBuilder:
    """
    This class provides an abstratction tu build a query for the ScanR elastic API
    """

    class SubjectType(Enum):
        """
        Types of subjects for which data can be retrieved from data.idref.fr
        """

        PERSON = "person"
        PUBLICATION = "publication"

    class QueryParameters(Enum):
        """
        Enum for named parameters used in main Person query
        """

        AUTH_IDREF = "idref"
        AUTH_ORCID = "orcid"
        AUTH_ID_HAL_S = "id_hal"

        PUBLICATION_AUTHOR = "authors.person"

    class IndexParameters(Enum):
        """
        Enum for recognized index in ScanR API
        """

        PERSONS_INDEX = 'scanr-persons'
        PUBLICATIONS_INDEX = 'scanr-publications'

    PERSON_DEFAULT_FIELDS = [
        "id",
        "externalIds",
        "domains",
        "affiliations",
        "fullName"
    ]

    PUBLICATIONS_DEFAULT_FIELDS = [
        "id",
        "title",
        "summary",
        "type",
        "productionType",
        "publicationDate",
        "domains",
        "affiliations",
        "authors",
        "externalIds"
    ]

    def __init__(self):
        self.index = None
        self.identifier_type = None
        self.identifier_value = None
        self.persons_fields = self.PERSON_DEFAULT_FIELDS
        self.publications_fields = self.PUBLICATIONS_DEFAULT_FIELDS
        self.subject_type: ScanRApiQueryBuilder.SubjectType | None = None
        self.query = {}

    def set_subject_type(self, subject_type: SubjectType):
        """
        Set the type of subject about which data will be retrieved : person or publication
        :param subject_type: the type of subject
        :return: the query builder
        """
        self.subject_type = subject_type
        return self

    def old_set_query(self,
                  index: IndexParameters,
                  identifier_type: QueryParameters, identifier_value):
        """
       Set the field name and value representing the entity for which the query is built.

       :param index: the index who will receive the built query
       :param identifier_type: the name of the field, from the QueryParameters enum
       :param identifier_value: the value of the field
       :return: None
       """
        # Check if the index who will receive the query is known
        assert index in self.IndexParameters, "That index is not referenced in ScanR API"

        # check that identifier_type is a valid QueryParameters
        assert identifier_type in self.QueryParameters, "Invalid identifier type"
        self.identifier_type = identifier_type
        self.identifier_value = identifier_value
        self.index = index

    def set_query(self,
                  identifier_type: QueryParameters, identifier_value):
        """
       Set the field name and value representing the entity for which the query is built.

       :param identifier_type: the name of the field, from the QueryParameters enum
       :param identifier_value: the value of the field
       :return: None
       """
        # Check if the index who will receive the query is known

        # check that identifier_type is a valid QueryParameters
        assert identifier_type in self.QueryParameters, "Invalid identifier type"
        self.identifier_type = identifier_type
        self.identifier_value = identifier_value

    def temp_idref_build(self):
        """
                Main building method, return a query DSL for the elastic ScanR API
                :return: a query dict
                """
        self.query["_source"] = self.PUBLICATIONS_DEFAULT_FIELDS
        person_value = self.identifier_type.value + self.identifier_value
        query_param = {
            "bool": {
                "must": [
                    {"term": {"authors.person": person_value}},
                ]
            }
        }

        self.query["query"] = query_param

        return self.query
    def build(self) -> dict:
        """
        Main building method, return a query DSL for the elastic ScanR API
        :return: a query dict
        """
        self._source_param()
        self._query_param()

        return self.query

    def _query_param(self):
        assert (
                self.identifier_type is not None and self.identifier_value is not None
        ), "Set the query parameters before building the query."

        query_param = {}
        if self.index == self.IndexParameters.PERSONS_INDEX:
            query_param = {
                "bool": {
                    "must": [
                        {"term": {"externalIds.type.keyword": self.identifier_type.value}},
                        {"term": {"externalIds.id.keyword": self.identifier_value}}
                    ]
                }
            }

        if self.index == self.IndexParameters.PUBLICATIONS_INDEX:
            query_param = {
                "bool": {
                    "must": [
                        {"term": {self.identifier_type.value: self.identifier_value}},
                    ]
                }
            }

        self.query["query"] = query_param

    def _source_param(self):
        returned_fields = []
        if self.index == self.IndexParameters.PERSONS_INDEX:
            returned_fields = self.PERSON_DEFAULT_FIELDS
        if self.index == self.IndexParameters.PUBLICATIONS_INDEX:
            returned_fields = self.PUBLICATIONS_DEFAULT_FIELDS

        self.query["_source"] = returned_fields
