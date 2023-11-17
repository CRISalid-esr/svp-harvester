from enum import Enum


class ScanRApiQueryBuilder:
    """
    This class provides an abstratction tu build a query for the ScanR elastic API
    """

    class QueryParameters(Enum):
        """
        Enum for named parameters used in main Person query
        """

        PERSON_ID_HAL_S = "id_hal"
        PERSON_ORCID_ID = "orcid"
        PERSON_IDREF = "idref"

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
        self.query = {}

    def set_query(self,
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
