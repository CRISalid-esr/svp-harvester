import pytest_asyncio

from app.db.models.reference_event import ReferenceEvent as DbReferenceEvent


@pytest_asyncio.fixture(name="reference_event_db_model")
async def fixture_reference_event_db_model(
    reference_db_model, harvesting_db_model_for_person_with_idref
) -> DbReferenceEvent:
    """
    Create a reference event db model

    :param reference_db_model: reference db model
    :param harvesting_db_model_for_person_with_idref: harvesting db model
    :return:
    """
    reference_event = DbReferenceEvent(type="created")
    reference_event.reference = reference_db_model
    reference_event.harvesting = harvesting_db_model_for_person_with_idref
    return reference_event
