"""Test the entity resolution API."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.harvesting import Harvesting
from app.db.models.reference import Reference as DbReference
from app.db.models.reference_event import ReferenceEvent
from app.db.models.title import Title
from app.db.references.references_recorder import ReferencesRecorder


@pytest.mark.asyncio
async def test_reference_recorder_creates_event_for_new_reference(
    async_session: AsyncSession, harvesting_db_model: Harvesting
):
    """
    GIVEN a currently running harvesting
    WHEN a new reference is registered
    THEN a reference event pointing to the new reference is created

    :param async_session:
    :param harvesting_db_model:
    :return:
    """
    # find harvesting_db_model in db
    async_session.add(harvesting_db_model)
    await async_session.commit()
    harvester = harvesting_db_model.harvester
    source_identifier = "source_identifier_1234"
    reference = DbReference(
        source_identifier=source_identifier,
        harvester=harvester,
        hash="hash1",
        titles=[Title(value="title", language="fr")],
    )
    reference_event: ReferenceEvent = await ReferencesRecorder().register(
        harvesting_id=harvesting_db_model.id,
        new_ref=reference,
        existing_references_source_identifiers=[],
    )
    assert reference_event is not None
    assert reference_event.reference == reference
    assert reference_event.reference.version == 0
    assert reference_event.harvesting_id == harvesting_db_model.id
    assert reference_event.type == ReferenceEvent.Type.CREATED.value


@pytest.mark.asyncio
async def test_reference_recorder_creates_event_for_updated_reference(
    async_session: AsyncSession, harvesting_db_model: Harvesting
):
    """
    GIVEN a reference in database with source_identifier and harvester
    WHEN the reference  with same source_identifier and harvester
        is registered again with a different hash
    THEN a reference event of "updated" type is created and a Reference
        with an incremented version number is created
    :param async_session:
    :param harvesting_db_model:
    :return:
    """
    # find harvesting_db_model in db
    async_session.add(harvesting_db_model)
    await async_session.commit()
    harvester = harvesting_db_model.harvester
    source_identifier = "source_identifier_1234"
    reference = DbReference(
        source_identifier=source_identifier,
        harvester=harvester,
        hash="hash1",
        titles=[Title(value="title", language="fr")],
        version=0,
    )
    async_session.add(reference)
    await async_session.commit()
    # update reference
    other_reference = DbReference(
        source_identifier=source_identifier,
        harvester=harvester,
        hash="hash2",
        titles=[Title(value="changed_title", language="fr")],
    )
    reference_event: ReferenceEvent = await ReferencesRecorder().register(
        harvesting_id=harvesting_db_model.id,
        new_ref=other_reference,
        existing_references_source_identifiers=[],
    )
    assert reference_event is not None
    assert reference_event.reference == other_reference
    assert reference_event.reference.version == 1
    assert reference_event.harvesting_id == harvesting_db_model.id
    assert reference_event.type == ReferenceEvent.Type.UPDATED.value
