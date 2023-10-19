"""Test that references API creates Retrieval in database."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.retrieval import Retrieval

pytestmark = pytest.mark.integration

REFERENCES_RETRIEVAL_API_PATH = "/api/v1/references/retrieval"


@pytest.mark.current
@pytest.mark.asyncio
async def test_fetch_references_async_with_event_types(
    test_client: TestClient,
    person_with_name_and_idref_json,
    async_session: AsyncSession,
):
    """Test the create_retrieval_sync endpoint."""
    response = test_client.post(
        REFERENCES_RETRIEVAL_API_PATH,
        json={
            "person": person_with_name_and_idref_json,
            "events": ["created", "updated"],
        },
    )
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["retrieval_id"] is not None
    retrieval_id = int(json_response["retrieval_id"])
    # get the retrieval from the database
    retrieval: Retrieval = (
        (
            await async_session.execute(
                select(Retrieval).filter(Retrieval.id == retrieval_id)
            )
        )
        .unique()
        .scalar_one_or_none()
    )
    assert retrieval is not None
    assert retrieval.event_types == ["created", "updated"]
