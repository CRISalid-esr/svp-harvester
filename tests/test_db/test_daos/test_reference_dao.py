"""Tests for entity dao."""
from typing import List

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.daos.reference_dao import ReferenceDAO
from app.db.models.harvesting import Harvesting
from app.db.models.reference import Reference as DbReference
from app.db.models.reference_event import ReferenceEvent
from app.db.models.title import Title


@pytest.mark.asyncio
async def test_get_references_by_source_identifier(
    async_session: AsyncSession, harvesting_db_model_for_person_with_idref: Harvesting
):
    """
    GIVEN two references in database with the same source identifier and successive version numbers
    WHEN get_references_by_source_identifier is called with the source identifier
    THEN the references are returned
    """
    harvester = harvesting_db_model_for_person_with_idref.harvester
    source_identifier = "source_identifier_1234"
    reference1 = DbReference(
        source_identifier=source_identifier,
        harvester=harvester,
        hash="hash1",
        version=0,
        titles=[Title(value="title", language="fr")],
    )
    reference2 = DbReference(
        source_identifier=source_identifier,
        harvester=harvester,
        hash="hash2",
        version=1,
        titles=[Title(value="changed_title", language="fr")],
    )
    async_session.add_all([reference1, reference2])
    await async_session.commit()
    dao = ReferenceDAO(async_session)

    references = await dao.get_references_by_source_identifier(
        harvester=harvester, source_identifier=source_identifier
    )

    assert references == [reference1, reference2]


@pytest.mark.asyncio
async def test_get_last_reference_by_source_identifier(
    async_session: AsyncSession, harvesting_db_model_for_person_with_idref
):
    """
    GIVEN two references in database with the same source identifier and successive version numbers
    WHEN get_last_reference_by_source_identifier is called with the source identifier
    THEN the last reference is returned
    """
    harvester = harvesting_db_model_for_person_with_idref.harvester
    source_identifier = "source_identifier_1234"
    reference1 = DbReference(
        source_identifier=source_identifier,
        harvester=harvester,
        hash="hash1",
        version=0,
        titles=[Title(value="title", language="fr")],
    )
    reference2 = DbReference(
        source_identifier=source_identifier,
        harvester=harvester,
        hash="hash2",
        version=1,
        titles=[Title(value="changed_title", language="fr")],
    )
    async_session.add_all([reference1, reference2])
    await async_session.commit()
    dao = ReferenceDAO(async_session)

    reference = await dao.get_last_reference_by_source_identifier(
        harvester=harvester, source_identifier=source_identifier
    )

    assert reference == reference2
    assert reference.titles[0].value == "changed_title"


@pytest.mark.asyncio
async def test_get_references_for_entity_and_harvester_only_returns_last_version(
    async_session: AsyncSession,
    two_completed_harvestings_db_models_for_same_person: List[Harvesting],
):
    """
    GIVEN two references in database with the same source identifier and successive version numbers
    WHEN get_references_for_entity_and_harvester is called with the source identifier
    THEN the last reference is returned
    """
    (
        harvesting_db_model_1,
        harvesting_db_model_2,
    ) = two_completed_harvestings_db_models_for_same_person
    source_identifier = "source_identifier_1234"
    harvester = harvesting_db_model_1.harvester  # the same for both
    reference1 = DbReference(
        source_identifier=source_identifier,
        harvester=harvester,
        hash="hash1",
        version=0,
        titles=[Title(value="title", language="fr")],
    )
    reference2 = DbReference(
        source_identifier=source_identifier,
        harvester=harvester,
        hash="hash2",
        version=1,
        titles=[Title(value="changed_title", language="fr")],
    )
    reference_event_1 = ReferenceEvent(
        type=ReferenceEvent.Type.CREATED.value,
        reference=reference1,
        harvesting=harvesting_db_model_1,
    )
    reference_event_2 = ReferenceEvent(
        type=ReferenceEvent.Type.UPDATED.value,
        reference=reference2,
        harvesting=harvesting_db_model_2,
    )
    async_session.add_all(
        [reference1, reference2, reference_event_1, reference_event_2]
    )
    await async_session.commit()
    dao = ReferenceDAO(async_session)

    references = await dao.get_previous_references_for_entity_and_harvester(
        harvesting_id=harvesting_db_model_2.id + 1,
        harvester=harvester,
        entity_id=harvesting_db_model_1.retrieval.entity_id,  # the same for both
    )

    assert references == [reference2]
    assert references[0].titles[0].value == "changed_title"


@pytest.mark.asyncio
async def test_get_references_for_entity_and_harvester_does_not_return_deleted_reference(
    async_session: AsyncSession,
    three_completed_harvestings_db_models_for_same_person: List[Harvesting],
):
    """
    GIVEN two references in database with the same source identifier and successive version numbers
            where the last has been deleted
    WHEN get_references_for_entity_and_harvester is
    THEN no reference is returned
    """
    # three harvestings have taken place for the same person
    (
        harvesting_db_model_1,
        harvesting_db_model_2,
        harvesting_db_model_3,
    ) = three_completed_harvestings_db_models_for_same_person

    harvester = harvesting_db_model_1.harvester  # the same for both
    source_identifier = "source_identifier_1234"
    # the first one created the reference 1
    reference1 = DbReference(
        source_identifier=source_identifier,
        harvester=harvester,
        hash="hash1",
        version=0,
        titles=[Title(value="title", language="fr")],
    )
    reference_event_1 = ReferenceEvent(
        type=ReferenceEvent.Type.CREATED.value,
        reference=reference1,
        harvesting=harvesting_db_model_1,
    )
    # the second one updated the reference 1, creating the reference 2 with increased version number
    reference2 = DbReference(
        source_identifier=source_identifier,
        harvester=harvester,
        hash="hash2",
        version=1,
        titles=[Title(value="changed_title", language="fr")],
    )
    reference_event_2 = ReferenceEvent(
        type=ReferenceEvent.Type.UPDATED.value,
        reference=reference2,
        harvesting=harvesting_db_model_2,
    )
    # the third one deleted the reference 2
    reference_event_3 = ReferenceEvent(
        type=ReferenceEvent.Type.DELETED.value,
        reference=reference2,
        harvesting=harvesting_db_model_3,
    )
    async_session.add_all(
        [
            reference1,
            reference2,
            reference_event_1,
            reference_event_2,
            reference_event_3,
        ]
    )
    await async_session.commit()
    # now a 4th harvesting is taking place
    # and we want to retrieve the reference for the previous harvesting
    dao = ReferenceDAO(async_session)

    references = await dao.get_previous_references_for_entity_and_harvester(
        harvester=harvester,
        entity_id=harvesting_db_model_1.retrieval.entity.id,
        harvesting_id=harvesting_db_model_3.id + 1,
    )

    assert len(references) == 0


@pytest.mark.asyncio
async def test_get_references_for_entity_and_harvester_returns_updated_reference(
    async_session: AsyncSession,
    two_completed_harvestings_db_models_for_same_person: List[Harvesting],
):
    """
    GIVEN two references in database with the same source identifier and successive version numbers
    WHEN get_references_for_entity_and_harvester is called with the source identifier
    THEN the returned reference is the last one with the updated title
    """
    # two harvestings have taken place for the same person
    (
        harvesting_db_model_1,
        harvesting_db_model_2,
    ) = two_completed_harvestings_db_models_for_same_person

    harvester = harvesting_db_model_1.harvester  # the same for both
    source_identifier = "source_identifier_1234"
    # the first one created the reference 1
    reference1 = DbReference(
        source_identifier=source_identifier,
        harvester=harvester,
        hash="hash1",
        version=0,
        titles=[Title(value="title", language="fr")],
    )
    reference_event_1 = ReferenceEvent(
        type=ReferenceEvent.Type.CREATED.value,
        reference=reference1,
        harvesting=harvesting_db_model_1,
    )
    # the second one updated the reference 1, creating the reference 2 with increased version number
    reference2 = DbReference(
        source_identifier=source_identifier,
        harvester=harvester,
        hash="hash2",
        version=1,
        titles=[Title(value="changed_title", language="fr")],
    )
    reference_event_2 = ReferenceEvent(
        type=ReferenceEvent.Type.UPDATED.value,
        reference=reference2,
        harvesting=harvesting_db_model_2,
    )
    async_session.add_all(
        [reference1, reference2, reference_event_1, reference_event_2]
    )
    await async_session.commit()
    # now a 3th harvesting is taking place
    # and we want to retrieve the reference for the previous harvesting
    dao = ReferenceDAO(async_session)

    references = await dao.get_previous_references_for_entity_and_harvester(
        harvester=harvester,
        entity_id=harvesting_db_model_1.retrieval.entity.id,
        harvesting_id=harvesting_db_model_2.id + 1,
    )

    assert references == [reference2]
    assert references[0].titles[0].value == "changed_title"


@pytest.mark.asyncio
@pytest.mark.current
async def test_get_complete_reference_by_harvester_source_identifier_version(
    async_session: AsyncSession, harvesting_db_model_for_person_with_idref: Harvesting
):
    """
    GIVEN a reference in database with a source identifier and version number
    WHEN get_complete_reference_by_harvester_source_identifier_version is called with the source identifier and version number
    THEN the reference is returned
    """
    harvester = harvesting_db_model_for_person_with_idref.harvester
    source_identifier = "source_identifier_1234"
    version = 0
    reference = DbReference(
        source_identifier=source_identifier,
        harvester=harvester,
        hash="hash1",
        version=version,
        titles=[Title(value="title", language="fr")],
    )
    async_session.add(reference)
    await async_session.commit()
    dao = ReferenceDAO(async_session)

    reference_returned = (
        await dao.get_complete_reference_by_harvester_source_identifier_version(
            harvester=harvester,
            source_identifier=source_identifier,
            version=version,
        )
    )

    assert reference_returned == reference
    assert reference_returned.titles[0].value == "title"
