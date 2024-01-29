from elasticsearch import Elasticsearch, ElasticsearchException

from app.config import get_app_settings

try:
    app_settings = get_app_settings()

    # Create an Elasticsearch instance
    es = Elasticsearch(
        [app_settings.scanr_es_host],
        http_auth=(app_settings.scanr_es_user, app_settings.scanr_es_password),
        use_ssl=True,
        verify_certs=True,
        scheme="https",
    )
except ElasticsearchException as e:
    print(f"An error occurred while connecting to Elasticsearch: {e}")


def get_unique_values(selected_field: str = "authors.role", size: int = 100):
    aggregation_query = {
        "size": 0,
        "aggs": {
            "unique_values": {
                "terms": {"field": f"{selected_field}.keyword", "size": size}
            }
        },
    }

    # Perform the search using the aggregation query
    response = es.search(index="scanr-publications-staging", body=aggregation_query)

    # Access the aggregation results
    aggregation_results = response["aggregations"]["unique_values"]["buckets"]
    print(f"Number of unique occurrences: {len(aggregation_results)}")
    keys = [bucket["key"] for bucket in aggregation_results]
    print(sorted(keys))


if __name__ == "__main__":
    get_unique_values()
    # get_unique_values(selected_field="type")
    # get_unique_values(selected_field="productionType")
