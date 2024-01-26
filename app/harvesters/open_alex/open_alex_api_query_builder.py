from enum import Enum
from urllib.parse import urlencode


class OpenAlexQueryBuilder:
    """
    This class is responsible for building the query to be sent to the OpenAlex API.
    """

    class SubjectType(Enum):
        """
        Enum for the subject type of the query
        """

        PERSON = "author"

    class QueryParameters(Enum):
        """
        Enum for named parameters used in main query
        """

        AUTH_ORCID = "orcid"

    def __init__(self) -> None:
        self.identifier_type = None
        self.identifier_value = None
        self.subject_type = None

    def set_query(
        self, identifier_type: QueryParameters, identifier_value: str
    ) -> None:
        """
        Set the field name and value representing the entity for which the query is built.

        :param identifier_type: the name of the field, from the QueryParameters enum
        :param identifier_value: the value of the field
        :return: None
        """

        assert identifier_type in self.QueryParameters, "Invalid identifier type"
        self.identifier_type = identifier_type
        self.identifier_value = identifier_value
        # TODO DOC TYPES AND SORT ?

    def build(self) -> str:
        """
        Main building method, returns a query string for the OpenAlex API.
        :return: a query string
        """

        params = self._query_param()
        return urlencode(params)

    def _query_param(self):
        assert (
            self.identifier_type is not None and self.identifier_value is not None
        ), "Set the query parameters before building the query."
        if self.subject_type == self.SubjectType.PERSON:
            return self._person_queries()
        else:
            raise NotImplementedError()

    def _person_queries(self):
        return {
            "filter": f"author.{self.identifier_type.value}:{self.identifier_value}"
        }

    def set_subject_type(self, subject_type: SubjectType):
        """
        Set the subject type of the query
        """
        self.subject_type = subject_type
