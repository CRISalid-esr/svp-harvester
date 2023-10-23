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
    references_recorder = ReferencesRecorder(harvesting=harvesting_db_model)
    assert (await references_recorder.exists(reference)) is None
    reference_event: ReferenceEvent = await references_recorder.register_creation(
        new_ref=reference,
    )
    assert reference_event is not None
    assert reference_event.reference == reference
    assert reference_event.reference.version == 0
    assert reference_event.harvesting_id == harvesting_db_model.id
    assert reference_event.type == ReferenceEvent.Type.CREATED.value


@pytest.mark.asyncio
async def test_reference_recorder_creates_event_for_updated_reference(
    async_session: AsyncSession,
    three_completed_harvestings_db_models_for_same_person: list[Harvesting],
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
    (
        harvesting_1,
        harvesting_2,
        harvesting_3,
    ) = three_completed_harvestings_db_models_for_same_person
    harvesting_3.status = Harvesting.State.RUNNING
    async_session.add_all([harvesting_1, harvesting_2, harvesting_3])
    await async_session.commit()
    harvester = harvesting_3.harvester  # same harvester for all harvestings
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
    new_version_of_reference = DbReference(
        source_identifier=source_identifier,
        harvester=harvester,
        hash="hash2",
        titles=[Title(value="changed_title", language="fr")],
    )
    references_recorder = ReferencesRecorder(harvesting=harvesting_3)
    old_reference = await references_recorder.exists(reference)
    assert old_reference is not None
    reference_event: ReferenceEvent = await references_recorder.register_update(
        old_ref=old_reference,
        new_ref=new_version_of_reference,
    )
    assert reference_event is not None
    assert reference_event.reference == new_version_of_reference
    assert reference_event.reference.version == 1
    assert reference_event.harvesting_id == harvesting_3.id
    assert reference_event.type == ReferenceEvent.Type.UPDATED.value
