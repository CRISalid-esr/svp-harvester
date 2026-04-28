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


@pytest_asyncio.fixture(name="reference_event_db_model_with_identifier_used")
async def fixture_reference_event_db_model_with_identifier_used(
    reference_db_model, harvesting_db_model_for_person_with_idref_and_identifier_used
) -> DbReferenceEvent:
    """
    Create a reference event db model linked to a harvesting with identifier_used fields set.

    :param reference_db_model: reference db model
    :param harvesting_db_model_for_person_with_idref_and_identifier_used: harvesting db model
    :return:
    """
    reference_event = DbReferenceEvent(type="created")
    reference_event.reference = reference_db_model
    reference_event.harvesting = harvesting_db_model_for_person_with_idref_and_identifier_used
    return reference_event
