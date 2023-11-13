from typing import Dict
from elasticsearch import Elasticsearch
from pydantic_settings import BaseSettings


class ScanRElasticClient:
    """Client for ScanR elastic API"""
    class ElasticSettings(BaseSettings):
        """Settings to access ScanR API"""
        ES_HOST: str
        ES_PUBLICATIONS_INDEX: str
        ES_PERSONS_INDEX: str
        ES_USER: str
        ES_PASS: str

        class Config:
            """
            Configuration for the ElasticSettings.
            Specifies the environment file and its encoding.
            """
            env_file = "./elastic.env"
            env_file_encoding = 'utf-8'

    def __init__(self):
        self.settings = self.ElasticSettings()

        self.elastic = Elasticsearch(
            [self.settings.ES_HOST],
            http_auth=(self.settings.ES_USER, self.settings.ES_PASS),
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

    def perform_search_persons(self):
        """
        Perform a search request on Scanr Person index and return the results
        :return: the result as list
        """
        count = self._count_references(index=self.settings.ES_PERSONS_INDEX)
        request = self.elastic.search(
            index=self.settings.ES_PERSONS_INDEX, body=self.query, size=count)
        cleaned_results = self._clean_results(request)
        return cleaned_results

    def perform_search_publications(self):
        """
        Perform a search request on Scanr Publication index and return the results
        :return: the result as list
        """
        count = self._count_references(index=self.settings.ES_PUBLICATIONS_INDEX)
        request = self.elastic.search(
            index=self.settings.ES_PUBLICATIONS_INDEX, body=self.query, size=count)
        cleaned_results = self._clean_results(request)
        return cleaned_results

    def _count_references(self, index):
        count = self.elastic.count(index=index, body=self.query)["count"]
        print(count)
        if count <= 1:
            return count
        raise ValueError("No references found with that query")

    def _clean_results(self, results):
        return results["hits"]["hits"]
