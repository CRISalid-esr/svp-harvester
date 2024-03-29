from enum import Enum
from typing import Dict, List

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import AuthenticationException, ElasticsearchException

from app.config import get_app_settings
from app.harvesters.exceptions.external_endpoint_failure import ExternalEndpointFailure
from app.harvesters.exceptions.unexpected_format_exception import (
    UnexpectedFormatException,
)


class ScanRElasticClient:
    """Client for ScanR elastic API"""

    class Indexes(Enum):
        """
        Indexes available for search with ScanR API
        """

        PERSONS = "scanr-persons"
        PUBLICATIONS = "scanr-publications"

    def __init__(self):
        self.settings = get_app_settings()
        self.query = None
        self.elastic = None

    async def __aenter__(self):
        self.elastic = AsyncElasticsearch(
            [self.settings.scanr_es_host],
            http_auth=(self.settings.scanr_es_user, self.settings.scanr_es_password),
            use_ssl=True,
            verify_certs=True,
            scheme="https",
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.elastic.close()
        self.elastic = None

    def set_query(self, elastic_query: Dict[str, any]):
        """
        Sets the Elasticsearch query for the ScanRElasticClient instance.

        Parameters:
            elastic_query (Dict[str, any]): The Elasticsearch query to be set.
        """
        self.query = elastic_query

    async def perform_search(self, selected_index: Indexes, base_size: int = 200):
        """
        Perform a search request on Scanr index and return the results
        :return: the result as list
        """

        async def search_and_yield(offset):
            nonlocal total_search_hits
            try:
                # pylint: disable=unexpected-keyword-arg
                resp = await self.elastic.search(
                    # "size" belongs to method parameters
                    # https://elasticsearch-py.readthedocs.io/en/v8.12.0/api/elasticsearch.html
                    # "from" is listed in documentation but appears as "from_" in library code
                    index=target_index,
                    body=self.query,
                    size=base_size,
                    from_=offset,
                )
            except AuthenticationException as exc:
                raise ExternalEndpointFailure(
                    "Invalid credentials for ScanR API"
                ) from exc
            except ElasticsearchException as exc:
                raise ExternalEndpointFailure("Unable to connect to ScanR API") from exc

            cleaned_results = self._clean_results(resp)  # clean the results

            total = resp.get("hits", {}).get("total", {}).get("value", 0)
            if total > total_search_hits:
                total_search_hits = total

            for result in cleaned_results:
                yield result

        assert selected_index in self.Indexes, "Selected index is unavailable"
        target_index = selected_index.value

        assert self.query, "Set a query before performing a search"

        total_search_hits = 0
        result_yielded = 0

        async for result in search_and_yield(result_yielded):
            result_yielded += 1
            yield result

        while result_yielded < total_search_hits:
            async for result in search_and_yield(result_yielded):
                result_yielded += 1
                yield result

    def _clean_results(self, results: Dict) -> List[Dict]:
        try:
            return results.get("hits", {}).get("hits", [])
        except AttributeError as exc:
            raise UnexpectedFormatException(
                "Expected a dictionary with potentially nested 'hits' keys, but got something else."
            ) from exc
