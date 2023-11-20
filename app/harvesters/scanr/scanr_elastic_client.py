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

    # TODO: normalize perform_search to only keep one search and not one per index
    async def perform_search_persons(self):
        """
        Perform a search request on Scanr Person index and return the results
        :return: the result as list
        """
        target_index = self.settings.scanr_es_persons_index

        number_of_references = await self._count_references(target_index)

        resp = await self.elastic.search(
            index=target_index,
            body=self.query,
            size=number_of_references
        )

        cleaned_results = self._clean_results(resp)

        for result in cleaned_results:
            yield result

    async def perform_search_publications(self):
        """
        Perform a search request on Scanr Publication index and return the results
        :return: the result as list
        """
        target_index = self.settings.scanr_es_publications_index

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
        return results["hits"]["hits"]
