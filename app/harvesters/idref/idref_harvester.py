import asyncio
import re
import urllib
from enum import Enum
from typing import AsyncGenerator
from aiostream import stream
from loguru import logger

import uritools
from rdflib import URIRef

from app.harvesters.abstract_harvester import AbstractHarvester
from app.harvesters.exceptions.unexpected_format_exception import (
    UnexpectedFormatException,
)
from app.harvesters.idref.OpenEditionIdrefSparqlClient import OpenEditionSparqlClient
from app.harvesters.idref.idref_sparql_client import IdrefSparqlClient
from app.harvesters.idref.idref_sparql_query_builder import (
    IdrefSparqlQueryBuilder as QueryBuilder,
)
from app.harvesters.idref.open_edition_resolver import OpenEditionResolver
from app.harvesters.idref.rdf_resolver import RdfResolver
from app.harvesters.rdf_harvester_raw_result import (
    AbstractHarvesterRawResult as RawResult,
)
from app.harvesters.rdf_harvester_raw_result import RdfHarvesterRawResult as RdfResult
from app.harvesters.sparql_harvester_raw_result import (
    SparqlHarvesterRawResult as SparqlResult,
)


class IdrefHarvester(AbstractHarvester):
    """
    Harvester for data.idref.fl
    """

    SUDOC_URL_SUFFIX = "http://www.sudoc.fr/"
    OPEN_EDITION_SUFFIX = "http://journals.openedition.org/"
    SCIENCE_PLUS_URL_SUFFIX = "http://hub.abes.fr/"
    SCIENCE_PLUS_QUERY_SUFFIX = "https://scienceplus.abes.fr/sparql"
    MAX_SUDOC_PARALLELISM = 3

    supported_identifier_types = ["idref", "orcid"]

    class Formatters(Enum):
        """
        Source identifiers for idref, including secondary sources
        """

        SUDOC_RDF = "SUDOC_RDF"
        SCIENCE_PLUS_RDF = "SCIENCE_PLUS_RDF"
        HAL_JSON = "HAL_JSON"
        IDREF_SPARQL = "IDREF_SPARQL"
        OPEN_EDITION = "OPEN_EDITION"

    async def fetch_results(self) -> AsyncGenerator[RawResult, None]:
        builder = QueryBuilder()
        if (await self._get_entity_class_name()) == "Person":
            idref: str = (await self._get_entity()).get_identifier("idref")
            orcid: str = (await self._get_entity()).get_identifier("orcid")
            assert (
                idref is not None or orcid is not None
            ), "Idref or Orcid identifier required when harvesting publications from data.idref.fr"
            if idref is not None:
                builder.set_subject_type(QueryBuilder.SubjectType.PERSON).set_idref_id(
                    idref
                )
            if orcid is not None:
                builder.set_subject_type(QueryBuilder.SubjectType.PERSON).set_orcid(
                    orcid
                )
        pending_queries = set()
        num_sudoc_waiting_queries = 0

        tasks_gen = stream.combine.merge(
            OpenEditionSparqlClient().fetch_uri_publications(
                builder.build_person_openedition_query()
            ),
            IdrefSparqlClient().fetch_publications(builder.build()),
        )

        async for doc in tasks_gen:
            coro = self._secondary_query_process(doc)
            # TODO temporary semi-sequential implementation
            # Sudoc server does not support parallel querying beyond 5 parallel requests
            pending_queries.add(asyncio.create_task(coro))
            if doc["secondary_source"] == "SUDOC":
                num_sudoc_waiting_queries += 1
            if num_sudoc_waiting_queries >= self.MAX_SUDOC_PARALLELISM:
                num_sudoc_waiting_queries = 0
                while pending_queries:
                    done_queries, pending_queries = await asyncio.wait(
                        pending_queries, return_when=asyncio.ALL_COMPLETED
                    )
                for query in done_queries:
                    pub = await query
                    if pub:
                        yield pub
        # process remaining queries
        while pending_queries:
            done_queries, pending_queries = await asyncio.wait(
                pending_queries, return_when=asyncio.FIRST_COMPLETED
            )
            for query in done_queries:
                pub = await query
                if pub:
                    yield pub

    def _secondary_query_process(self, doc: dict):
        coro = None
        if doc["secondary_source"] == "IDREF":
            coro = self._convert_publication_from_idref_endpoint(doc)
        elif doc["secondary_source"] == "SUDOC":
            coro = self._query_publication_from_sudoc_endpoint(doc)
        elif doc["secondary_source"] == "HAL":
            coro = self._query_publication_from_hal_endpoint(doc)
        elif doc["secondary_source"] == "SCIENCE_PLUS":
            coro = self._query_publication_from_science_plus_endpoint(doc)
        elif doc["secondary_source"] == "OPEN_EDITION":
            coro = self._query_publication_from_openedition_endpoint(doc)
        else:
            logger.info(f"Unknown source {doc['secondary_source']}")
        return coro

    async def _query_publication_from_openedition_endpoint(self, doc: dict):
        """
        Query the publications from the OpenEdition API
        :param doc: the publication doc as result of the SPARQL query to data.idref.fr with the uri
        :return: the publication details
        """

        uri: str | None = doc.get("uri", "")
        if not uritools.isuri(uri):
            raise UnexpectedFormatException(
                f"Invalid OpenEdition URI from Idref SPARQL endpoint: {uri}"
            )
        assert uri.startswith(self.OPEN_EDITION_SUFFIX), "Invalid OpenEdition Id"
        client = OpenEditionResolver()
        pub = await client.fetch(uri)
        return RdfResult(
            payload=pub,
            source_identifier=URIRef(uri),
            formatter_name=self.Formatters.OPEN_EDITION.value,
        )

    async def _query_publication_from_sudoc_endpoint(self, doc: dict) -> RdfResult:
        """
        Query the details of a publication from the SUDOC API

        :param doc: the publication doc as result of the SPARQL query to data.idref.fr
        :return: the publication details
        """
        uri: str | None = doc.get("uri", "")
        if not uritools.isuri(uri):
            raise UnexpectedFormatException(
                f"Invalid SUDOC URI from Idref SPARQL endpoint: {uri}"
            )
        assert uri.startswith(self.SUDOC_URL_SUFFIX), "Invalid Sudoc Id"
        assert uri.endswith("/id"), "Provided Sudoc URI should end with /id"
        # with regular expression, replace trailing "/id" by '.rdf' in document_uri
        document_uri = re.sub(r"/id$", ".rdf", uri)
        # with regular expression, replace "http://" by "https://" in document_uri
        document_uri = re.sub(r"^http://", "https://", document_uri)
        client = RdfResolver()
        pub = await client.fetch(document_uri, output_format="xml")
        return RdfResult(
            payload=pub,
            source_identifier=URIRef(uri),
            formatter_name=self.Formatters.SUDOC_RDF.value,
        )

    async def _convert_publication_from_idref_endpoint(self, doc: dict) -> SparqlResult:
        """
        Query the details of a publication from the IDREF API

        :param doc: the publication doc
        :return: the publication details
        """
        return SparqlResult(
            payload=doc,
            source_identifier=URIRef(doc.get("uri")),
            formatter_name=self.Formatters.IDREF_SPARQL.value,
        )

    async def _query_publication_from_hal_endpoint(
        self, doc: dict  # pylint: disable=unused-argument
    ) -> RawResult:
        """
        Query the details of a publication from the HAL API

        :param doc: the publication doc
        :return: the publication details
        """
        return {}

    async def _query_publication_from_science_plus_endpoint(
        self, doc: dict  # pylint: disable=unused-argument
    ) -> RawResult:
        """
        Query the details of a publication from the Science+ API

        :param doc: the publication doc
        :return: the publication details
        """
        client = RdfResolver()
        uri: str | None = doc.get("uri", "")
        assert uri.startswith(self.SCIENCE_PLUS_URL_SUFFIX), "Invalid SciencePlus Id"
        if not uritools.isuri(uri):
            raise UnexpectedFormatException(
                f"Invalid SUDOC URI from Idref SPARQL endpoint: {uri}"
            )
        params = {
            "query": f'define sql:describe-mode "CBD"  DESCRIBE <{uri}>',
            "output": "application/rdf+xml",
        }
        # concatenate encoded params to query suffix
        query_uri = f"{self.SCIENCE_PLUS_QUERY_SUFFIX}?{urllib.parse.urlencode(params)}"
        pub = await client.fetch(query_uri, output_format="xml")
        return RdfResult(
            payload=pub,
            source_identifier=URIRef(uri),
            formatter_name=self.Formatters.SCIENCE_PLUS_RDF.value,
        )
