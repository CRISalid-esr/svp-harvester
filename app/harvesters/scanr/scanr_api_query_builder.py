from enum import Enum


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

    PERSON_DEFAULT_FIELDS = ["id", "externalIds", "domains", "affiliations", "fullName"]

    # This listing is independant from _hash_keys in ScanrReferencesConverter
    # pylint: disable=duplicate-code
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
        "externalIds",
    ]

    def __init__(self):
        self.identifier_type = None
        self.identifier_value = None
        self.scanr_id = None
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

    def _set_scanr_id(self):
        if self.identifier_type == self.QueryParameters.AUTH_IDREF:
            self.scanr_id = self.identifier_type.value + self.identifier_value

    def set_query(self, identifier_type: QueryParameters, identifier_value):
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

        self._set_scanr_id()

    def build(self) -> dict:
        """
        Main building method, return a query DSL for the elastic ScanR API
        :return: a query dict
        """
        self._source_param()
        self._query_param()
        self._sort_param()

        return self.query

    def _query_param(self):
        assert (
            self.identifier_type is not None and self.identifier_value is not None
        ), "Set the query parameters before building the query."

        if self.subject_type == self.SubjectType.PERSON:
            query_param = self._person_queries()

        elif self.subject_type == self.SubjectType.PUBLICATION:
            query_param = self._publication_queries()
        else:
            raise NotImplementedError()

        self.query["query"] = query_param

    def _person_queries(self):
        if self.scanr_id:
            query_param = {
                "bool": {
                    "must": [
                        {"term": {"id": self.scanr_id}},
                    ]
                }
            }
        elif self.identifier_type == self.QueryParameters.AUTH_ORCID:
            query_param = {
                "bool": {
                    "must": [
                        {"term": {self.identifier_type.value: self.identifier_value}},
                    ]
                }
            }
        else:
            query_param = {
                "bool": {
                    "must": [
                        {
                            "term": {
                                "externalIds.type.keyword": self.identifier_type.value
                            }
                        },
                        {"term": {"externalIds.id.keyword": self.identifier_value}},
                    ]
                }
            }

        return query_param

    def _publication_queries(self):
        if self.scanr_id:
            query_param = {
                "bool": {
                    "must": [
                        {"term": {"authors.person": self.scanr_id}},
                    ]
                }
            }
        else:
            raise NotImplementedError()
        return query_param

    def _source_param(self):
        returned_fields = []
        if self.subject_type == self.SubjectType.PERSON:
            returned_fields = self.PERSON_DEFAULT_FIELDS
        if self.subject_type == self.SubjectType.PUBLICATION:
            returned_fields = self.PUBLICATIONS_DEFAULT_FIELDS

        self.query["_source"] = returned_fields

    def _sort_param(self):
        sort = {"publicationDate": {"order": "desc"}}
        self.query["sort"] = sort
