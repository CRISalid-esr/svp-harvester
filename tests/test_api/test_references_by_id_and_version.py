"""Test the references API."""

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.reference import Reference as DbReference

REFERENCES_BY_ID_AND_VERSION_API_PATH = "/api/v1/references/by_id_and_version"


async def test_reference_version_comparaison_is_exhaustive(
    test_client: TestClient,
    async_session: AsyncSession,
    reference_version_0_without_details_db_model: DbReference,
    reference_version_1_with_details_db_model: DbReference,
):
    """Test the create_retrieval_sync endpoint."""
    async_session.add(reference_version_0_without_details_db_model)
    async_session.add(reference_version_1_with_details_db_model)
    await async_session.commit()
    version = 0
    response_1 = get_by_harvester_id_and_version(
        reference_version_0_without_details_db_model.harvester,
        reference_version_0_without_details_db_model.source_identifier,
        test_client,
        version,
    )
    assert response_1.status_code == 200
    version = 1
    response_2 = get_by_harvester_id_and_version(
        reference_version_0_without_details_db_model.harvester,
        reference_version_0_without_details_db_model.source_identifier,
        test_client,
        version,
    )
    assert response_2.status_code == 200

    json_reference_1 = response_1.json()
    json_reference_2 = response_2.json()
    assert json_reference_1["titles"] == [
        {"value": "Publication with poor description", "language": "en"}
    ]
    assert json_reference_2["titles"] == [
        {"value": "Publication with rich description", "language": "en"}
    ]
    assert len(json_reference_1["subtitles"]) == 0
    assert json_reference_2["subtitles"] == [{"value": "subtitle", "language": "en"}]
    assert json_reference_1["issued"] is None
    assert json_reference_2["issued"] == "2017-01-01T00:00:00"
    assert json_reference_1["created"] is None
    assert json_reference_2["created"] == "2018-02-02T10:00:00"
    assert json_reference_1["issue"] is None
    assert json_reference_2["issue"] == {
        "source": "openalex",
        "source_identifier": "https://openalex.org/s41586-021-03666-1",
        "titles": [],
        "volume": "50",
        "number": ["08"],
        "rights": "CC BY 4.0",
        "date": "2021",
        "journal": {
            "source": "openalex",
            "source_identifier": "https://openalex.org/S2764375719",
            "issn": ["0009-4978", "1523-8253", "1943-5975"],
            "eissn": [],
            "issn_l": "0009-4978",
            "publisher": "Association publishers",
            "titles": ["Scientific journal"],
        },
    }
    assert len(json_reference_1["subjects"]) == 0
    assert json_reference_2["subjects"] == [
        {
            "uri": "http://uri",
            "dereferenced": False,
            "pref_labels": [{"value": "label", "language": "fr"}],
            "alt_labels": [],
        }
    ]


def get_by_harvester_id_and_version(harvester, source_identifier, test_client, version):
    response = test_client.get(
        f"{REFERENCES_BY_ID_AND_VERSION_API_PATH}?"
        f"harvester={harvester}"
        f"&source_identifier={source_identifier}"
        f"&version={version}"
    )
    return response
