"""Test the references API."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.reference import Reference
from app.db.models.title import Title


@pytest.mark.current
async def test_get_references_by_harvester(
    test_client: TestClient, async_session: AsyncSession
):
    """
    Given a few references in the database
    When I request the references by harvester
    Then I should get a dict with harvester as key and a the number of references as value

    :param test_client:
    :return:
    """
    params = [("hal", 10), ("scopus", 5), ("idref", 3)]
    for harvester, count in params:
        for i in range(count):
            reference = Reference(
                source_identifier=f"source_identifier_{i}",
                harvester=harvester,
                hash="hash",
                version=0,
                titles=[Title(value="Fake scientific article", language="en")],
            )
            async_session.add(reference)
    await async_session.commit()
    response = test_client.get("/api/v1/metrics/references/by_harvester")
    assert response.status_code == 200
    data = response.json()
    assert data == {"hal": 10, "scopus": 5, "idref": 3}
