from typing import Dict, List
from elasticsearch import AsyncElasticsearch

from app.config import get_app_settings


class ScanRElasticClient:
    """Client for ScanR elastic API"""

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

    async def perform_search_persons(self):
        """
        Perform a search request on Scanr Person index and return the results
        :return: the result as list
        """
        resp = await self.elastic.search(
            index=self.settings.scanr_es_persons_index, body=self.query)
        cleaned_results = self._clean_results(resp)

        for result in cleaned_results:
            yield result

    async def perform_search_publications(self):
        """
        Perform a search request on Scanr Publication index and return the results
        :return: the result as list
        """
        resp = await self.elastic.search(
            index=self.settings.scanr_es_publications_index,
            body=self.query
        )

        cleaned_results = self._clean_results(resp)

        for result in cleaned_results:
            yield result

    def _clean_results(self, results: Dict) -> List[Dict]:
        return results["hits"]["hits"]
