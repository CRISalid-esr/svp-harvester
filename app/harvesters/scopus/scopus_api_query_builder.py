from enum import Enum
from urllib.parse import urlencode


class ScopusQueryBuilder:
    """
    This class is responsible for building the query to be sent to Scopu API.
    """

    class SubjectType(Enum):
        """
        Enum for the subject type of the query
        """

        PERSON = "person"

    class QueryParameters(Enum):
        """
        Enum for name parameters used in main query
        """

        SCOPUS_EID = "AU-ID"

    def __init__(self) -> None:
        self.identifier_type = None
        self.identifier_value = None
        self.subject_type = None

    def set_query(
        self, identifier_type: QueryParameters, identifier_value: str
    ) -> None:
        """
        Set the field name and value representing the entity for which the query is built.
        """

        assert identifier_type in self.QueryParameters, "Invalid identifier type"
        self.identifier_type = identifier_type
        self.identifier_value = identifier_value

    def build(self) -> str:
        """
        Main building method, returns a query string for the Scopus API
        """

        params = self._query_param()
        return urlencode(params)

    def _query_param(self):
        assert (
            self.identifier_type is not None and self.identifier_value is not None
        ), "Set the query parameters before building the query."

        if self.subject_type == self.SubjectType.PERSON:
            return self._person_queries()
        raise NotImplementedError

    def _person_queries(self):
        return {"query": f"{self.identifier_type.value}({self.identifier_value})"}

    def set_subject_type(self, subject_type: SubjectType):
        """
        Set the subject type of the query
        """
        self.subject_type = subject_type
