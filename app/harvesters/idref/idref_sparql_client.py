from enum import Enum
from typing import AsyncGenerator

import aiohttp
from aiosparql.client import SPARQLClient

from app.harvesters.exceptions.external_endpoint_failure import ExternalEndpointFailure

DATA_IDREF_FR_URL = "https://data.idref.fr/sparql"

IDREF_SPARQL_DEFAULT_TIMEOUT = 20


class IdrefSparqlClient:
    """Async client for data.idref.fr SPARQL API, wrapper around aiosparql"""

    def __init__(self, timeout: int = IDREF_SPARQL_DEFAULT_TIMEOUT):
        self.timeout = timeout

    class DataSources(Enum):
        """Typology of data sources for which data.idref.fr gathers data"""

        IDREF = "IDREF"
        HAL = "HAL"
        SUDOC = "SUDOC"
        SCIENCE_PLUS = "SCIENCE_PLUS"
        OPEN_EDITION = "OPEN_EDITION"
        PERSEE = "PERSEE"

    AUTHORS_PREFIXES = [
        "http://id.loc.gov/vocabulary/relators/",
        "http://www.abes.fr/vocabularies/theses/roles/",
    ]

    DATA_SOURCES_PREFIXES = {
        DataSources.IDREF: [
            "http://www.idref.fr/",
        ],
        DataSources.HAL: [
            "https://hal.archives-ouvertes.fr/",
        ],
        DataSources.SUDOC: [
            "http://www.sudoc.fr/",
        ],
        DataSources.SCIENCE_PLUS: [
            "http://hub.abes.fr/",
        ],
        DataSources.OPEN_EDITION: [
            "http://journals.openedition.org/",
            "https://journals.openedition.org/",
            "http://books.openedition.org/",
            "https://books.openedition.org/",
        ],
        DataSources.PERSEE: [
            "http://data.persee.fr/",
        ],
    }

    async def fetch_publications(self, query: str) -> AsyncGenerator[dict, None]:
        """
        Fetch publications list for a given author from the Idref sparql endpoint

        :param query:  the sparql query to send to the Idref sparql endpoint
        :return: A generator of results
        """
        client: SPARQLClient = self._get_client()
        try:
            response = await client.query(query)
            # aggregate results
            publications = {}
            for result in response.get("results", {}).get("bindings", []):
                if not any(
                    result.get("role", {}).get("value", "").startswith(prefix)
                    for prefix in self.AUTHORS_PREFIXES
                ):
                    continue
                pub = result.get("pub", {}).get("value", "")
                # create a new publication if it does not exist
                if pub not in publications:
                    publications[pub] = {
                        "uri": pub,
                        "role": result.get("role", {}).get("value", ""),
                        "contributor": [],
                        "contributorRole": [],
                        "contributorName": [],
                        "contributorFamilyName": [],
                        "contributorGivenName": [],
                        "title": [],
                        "note": [],
                        "type": [],
                        "altLabel": [],
                        "subject": {},
                        "equivalent": [],
                        "doi": result.get("doi", {}).get("value", ""),
                    }
                # add the data to the publication
                for key in [
                    "type",
                    "title",
                    "altLabel",
                    "note",
                    "contributor",
                    "contributorRole",
                    "contributorName",
                    "contributorFamilyName",
                    "contributorGivenName",
                    "equivalent",
                ]:
                    if (
                        result.get(key, {}).get("value", "")
                        not in publications[pub][key]
                    ):
                        publications[pub][key].append(
                            result.get(key, {}).get("value", "")
                        )
                subject_uri = result.get("subject_uri", {}).get("value", "")
                if subject_uri and subject_uri not in publications[pub]["subject"]:
                    publications[pub]["subject"][subject_uri] = {
                        "uri": subject_uri,
                        "label": result.get("subject_label", {}).get("value", ""),
                        "lang": result.get("subject_label", {}).get("xml:lang", ""),
                    }

            for publication in publications.values():
                yield publication | {
                    # identify the secondary source to which the publication belongs
                    "secondary_source": self._result_source_code(
                        publication.get("uri", "")
                    )
                }
        except Exception as error:
            raise ExternalEndpointFailure(
                "Error while fetching Idref sparql endpoint for query : "
                f"{query} with error {error.__class__.__name__} {error if error else ''}"
            ) from error

        finally:
            await client.close()

    async def fetch_publication(self, query: str) -> dict:
        """
        Fetch data for a single publication from the Idref sparql endpoint
        :param query: the sparql query to send to the Idref sparql endpoint
        :return: the result as dict
        """
        client: SPARQLClient = self._get_client()
        try:
            response = await client.query(query)
            print(query)
            pub_raw_data: dict = response.get("results", {}).get("bindings", [])
            # simplify the data structure by removing the first level of keys
            return {
                data.get("prop", {})
                .get("value", ""): data.get("val", {})
                .get("value", "")
                for data in pub_raw_data
            }
        except Exception as error:
            raise ExternalEndpointFailure(
                "Error while fetching Idref sparql endpoint for query : "
                f"{query} with error {error.__class__.__name__} {error if error else ''}"
            ) from error
        finally:
            await client.close()

    def _result_source_code(self, uri: str) -> str:
        for source, prefixes in self.DATA_SOURCES_PREFIXES.items():
            if any(uri.startswith(prefix) for prefix in prefixes):
                return source.value
        raise ExternalEndpointFailure(f"Unknown data source for uri {uri}")

    def _get_client(self) -> SPARQLClient:
        return SPARQLClient(
            DATA_IDREF_FR_URL,
            connector=aiohttp.TCPConnector(limit=0),
            timeout=aiohttp.ClientTimeout(total=float(self.timeout)),
        )
