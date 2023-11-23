from typing import Dict, List
from enum import Enum
from elasticsearch import AsyncElasticsearch

from app.config import get_app_settings
from app.harvesters.exceptions.unexpected_format_exception import UnexpectedFormatException


class ScanRElasticClient:
    """Client for ScanR elastic API"""

    class Indexes(Enum):
        """
        Indexes available for search with ScanR API
        """
        PERSONS = "scanr-persons-staging"
        PUBLICATIONS = "scanr-publications-staging"

    def __init__(self):
        self.settings = get_app_settings()

        self.elastic = AsyncElasticsearch(
            [self.settings.scanr_es_host],
            http_auth=(self.settings.scanr_es_user, self.settings.scanr_es_password),
            use_ssl=True,
            verify_certs=True,
            scheme="https",
        )

        self.query = None

    def set_query(self, elastic_query: Dict[str, any]):
        """
        Sets the Elasticsearch query for the ScanRElasticClient instance.

        Parameters:
            elastic_query (Dict[str, any]): The Elasticsearch query to be set.
        """
        self.query = elastic_query

    async def perform_search(self, selected_index: Indexes):
        """
        Perform a search request on Scanr index and return the results
        :return: the result as list
        """
        assert selected_index in self.Indexes, "Selected index is unavailable"
        target_index = selected_index.value

        number_of_references = await self._count_references(target_index)

        resp = await self.elastic.search(
            index=target_index,
            body=self.query,
            size=number_of_references
        )

        cleaned_results = self._clean_results(resp)

        for result in cleaned_results:
            yield result

    async def _count_references(self, index):
        count_query = self.query.copy()
        count_query.pop('_source', None)
        count_query.pop('sort', None)

        response = await self.elastic.count(index=index, body=count_query)
        count = response["count"]
        print(count)
        if count >= 1:
            return count
        raise ValueError("No references found with that query")

    def _clean_results(self, results: Dict) -> List[Dict]:
        try:
            return results.get("hits", {}).get("hits", [])
        except AttributeError as exc:
            raise UnexpectedFormatException(
                "Expected a dictionary with potentially nested 'hits' keys, but got something else."
            ) from exc
