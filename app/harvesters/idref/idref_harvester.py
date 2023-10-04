from enum import Enum
from typing import AsyncGenerator

import uritools
from pydantic import BaseModel
from rdflib import URIRef

from app.harvesters.abstract_harvester import AbstractHarvester
from app.harvesters.exceptions.unexpected_format_exception import (
    UnexpectedFormatException,
)
from app.harvesters.idref.data_idref_fr_sparql_client import DataIdrefFrSparqlClient
from app.harvesters.idref.data_idref_fr_sparql_query_builder import (
    DataIdrefFrSparqlQueryBuilder as QueryBuilder,
)
from app.harvesters.idref.sudoc_api_client import SudocApiClient
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

    class Formatters(Enum):
        """
        Source identifiers for idref, including secondary sources
        """

        SUDOC_RDF = "SUDOC_RDF"
        HAL_JSON = "HAL_JSON"
        IDREF_SPARQL = "IDREF_SPARQL"

    async def fetch_results(self) -> AsyncGenerator[RawResult, None]:
        builder = QueryBuilder()
        if (await self._get_entity_class_name()) == "Person":
            idref: str = (await self._get_entity()).get_identifier("idref")
            assert (
                idref is not None
            ), "Idref identifier is required when harvesting publications from data.idref.fr"
            builder.set_subject_type(QueryBuilder.SubjectType.PERSON).set_idref_id(
                idref
            )
        # pending_queries = []
        async for doc in DataIdrefFrSparqlClient().fetch_publications(builder.build()):
            coro = None
            if doc["secondary_source"] == "IDREF":
                pass
                # coro = self._query_publication_from_idref_endpoint(doc)
            elif doc["secondary_source"] == "SUDOC":
                coro = self._query_publication_from_sudoc_endpoint(doc)
            elif doc["secondary_source"] == "HAL":
                coro = self._query_publication_from_hal_endpoint(doc)
            else:
                print(f"Unknown source {doc['secondary_source']}")
                continue
            # TODO temporary sequential implementation
            # Sudoc server does not support parallel querying
            #     pending_queries.append(asyncio.create_task(coro))
            # while pending_queries:
            #     done_queries, pending_queries = await asyncio.wait(
            #         pending_queries, return_when=asyncio.FIRST_COMPLETED
            #     )
            #     done_queries
            #     for query in done_queries:
            #         pub = await query
            #         if pub:
            #             yield pub
            if not coro:
                continue
            pub = await coro
            if pub:
                yield pub

    async def _query_publication_from_sudoc_endpoint(self, doc: dict) -> RdfResult:
        """
        Query the details of a publication from the SUDOC API

        :param doc: the publication doc as result of the SPARQL query to data.idref.fr
        :return: the publication details
        """
        uri: str | None = doc.get("pub", {}).get("value")
        if not uritools.isuri(uri):
            raise UnexpectedFormatException(
                f"Invalid SUDOC URI from Idref SPARQL endpoint: {uri}"
            )
        client = SudocApiClient()
        pub = await client.fetch(uri)
        return RdfResult(
            payload=pub,
            source_identifier=URIRef(uri),
            formatter_name=self.Formatters.SUDOC_RDF.value,
        )

    async def _query_publication_from_idref_endpoint(self, doc: dict) -> SparqlResult:
        """
        Query the details of a publication from the IDREF API

        :param doc: the publication doc
        :return: the publication details
        """
        uri = doc["pub"]["value"]
        builder = (
            QueryBuilder()
            .set_subject_type(QueryBuilder.SubjectType.PUBLICATION)
            .set_subject_uri(uri)
        )
        raw_data = await DataIdrefFrSparqlClient().fetch_publication(builder.build())
        return SparqlResult(
            payload=raw_data,
            source_identifier=URIRef(uri),
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

    def is_relevant(self, entity: BaseModel) -> bool:
        return entity.get_identifier("idref") is not None
