"""Test the references API."""
from datetime import datetime
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.harvesting import Harvesting
from app.db.models.reference import Reference
from app.db.models.reference_event import ReferenceEvent
from app.db.models.title import Title


async def test_get_references_by_harvester(
    test_client: TestClient, async_session: AsyncSession
):
    """
    Given a few references in the database
    When I request the references by harvester
    Then I should get a dict with harvester as key and a the number of references as value

    :param test_client:
    :param async_session:
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


async def test_get_reference_events_by_day_and_type(
    test_client: TestClient,
    async_session: AsyncSession,
    harvesting_db_model_for_person_with_idref: Harvesting,
):
    """
    Given a few reference events in the database
    When I request the reference events by day and type
    Then I should get a dict with day as key and a dict with event type as key and number of events as value

    :param test_client:
    :param async_session:
    :return:
    """
    references = []

    recent_date = datetime.today() - timedelta(days=2)
    for i in range(10):
        reference = Reference(
            source_identifier=f"source_identifier_{i}",
            harvester="hal",
            hash="hash",
            version=0,
            titles=[Title(value="Fake scientific article", language="en")],
        )
        references.append(reference)
        async_session.add(reference)
        harvesting_db_model_for_person_with_idref.timestamp = recent_date
        async_session.add(harvesting_db_model_for_person_with_idref)
    events_by_day = {
        "23-03-2024": {"updated": 6, "created": 4, "deleted": 2},
    }
    reference_number = 0
    for day, events in events_by_day.items():
        for event_type, count in events.items():
            for i in range(count):
                reference_number += 1
                reference_event = ReferenceEvent(
                    type=event_type,
                    harvesting=harvesting_db_model_for_person_with_idref,
                    reference=references[reference_number % len(references)],
                )
                async_session.add(reference_event)
    await async_session.commit()
    response = test_client.get("/api/v1/metrics/reference_events/by_day_and_type")
    assert response.status_code == 200
    data = response.json()

    recent_date_str = recent_date.strftime("%d-%m-%Y")
    assert data == {recent_date_str: {"created": 4, "deleted": 2, "updated": 6}}
