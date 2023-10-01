from enum import Enum

import uritools
from aiosparql.syntax import Namespace, PrefixedName, IRI


class DataIdrefFrSparqlQueryBuilder:
    """
    This class provides an abstraction to build a query for data.idref.fr sparql endpoint
    """

    class SubjectType(Enum):
        """
        Types of subjects for which data can be retrieved from data.idref.fr
        """

        PERSON = "person"
        PUBLICATION = "publication"

    class Marcrel(Namespace):
        """
        MARC relator codes
        """

        __iri__ = IRI("http://id.loc.gov/vocabulary/relators/")
        author = PrefixedName

    def __init__(self) -> None:
        self.subject_uri: str = None
        self.subject_type: DataIdrefFrSparqlQueryBuilder.SubjectType | None = None

    def set_idref_id(self, idref_id: str):
        """
        Set the subject uri from an idref id

        :param idref_id: the idref id of the subject
        :return: the query builder
        """
        self.subject_uri = f"http://www.idref.fr/{idref_id}/id"
        return self

    def set_subject_type(self, subject_type: SubjectType):
        """
        Set the type of subject about which data will be retrieved : person or publication
        :param subject_type: the type of subject
        :return: the query builder
        """
        self.subject_type = subject_type
        return self

    def set_subject_uri(self, subject_uri: str):
        """
        Disrectly set the subject uri
        :param subject_uri: the subject uri
        :return: the query builder
        """
        assert uritools.isuri(subject_uri), f"{subject_uri} is not a valid URI"
        self.subject_uri = subject_uri
        return self

    def build(self):
        """
        Build the SPARQL query
        :return: the query
        """
        assert (
            self.subject_type is not None
        ), "Specify a subject type before building the query"
        assert self.subject_uri is not None, (
            "Specify a subject uri or an idref id for the subject "
            "before building the query"
        )
        if self.subject_type == DataIdrefFrSparqlQueryBuilder.SubjectType.PERSON:
            return self._build_person_query()
        if self.subject_type == DataIdrefFrSparqlQueryBuilder.SubjectType.PUBLICATION:
            return self._build_publication_query()
        raise ValueError(f"Unknown subject type {self.subject_type}")

    def _build_person_query(self) -> str:
        return (
            "select distinct ?pub ?role "  # caution: trailing space is important
            f"where {{?pub ?role <{self.subject_uri}>}}\n"
            "LIMIT 10000"
        )

    def _build_publication_query(self) -> str:
        return (
            "select distinct ?prop ?val "  # caution: trailing space is important
            f"where {{<{self.subject_uri}> ?prop ?val}}\n"
            "LIMIT 10000"
        )
