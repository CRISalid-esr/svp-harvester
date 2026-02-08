"""Tests for the Person model."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.models.issue import Issue
from app.db.models.journal import Journal
from app.db.models.reference import Reference
from app.db.models.title import Title
from app.harvesters.hal.hal_custom_metadata_schema import HalCustomMetadataSchema


@pytest.mark.asyncio
async def test_orphan_titles_deletion(async_session: AsyncSession):
    """
    GIVEN a reference with a title
    WHEN the reference is deleted
    THEN the title is deleted
    """
    title = Title(value="title", language="fr")
    reference = Reference(
        source_identifier="source_identifier_1234",
        harvester="harvester",
        hash="hash",
        version=0,
        titles=[title],
    )
    async_session.add(reference)
    await async_session.commit()
    title_id = title.id
    await async_session.delete(reference)
    await async_session.commit()
    query = select(Title).where(Title.id == title_id)
    title: Title = (await async_session.execute(query)).scalar()
    assert title is None


async def test_reference_with_issue_and_journal(async_session: AsyncSession):
    """
    GIVEN a reference with an issue and a journal
    WHEN the reference is created
    THEN check the reference has the correct attributes
    """
    journal = Journal(
        source="source",
        source_identifier="source_identifier_1234",
        titles=["Fake scientific journal"],
        issn="1234-5678",
    )
    issue = Issue(
        source="source",
        source_identifier="source_identifier_1234",
        volume="1",
        number=["1"],
        date="2021",
        journal=journal,
    )
    reference = Reference(
        source_identifier="source_identifier_1234",
        harvester="harvester",
        hash="hash",
        version=0,
        titles=[Title(value="Fake scientific article", language="en")],
        issue=issue,
    )
    async_session.add(reference)
    await async_session.commit()
    reference_id = reference.id
    journal_id = journal.id
    issue_id = issue.id
    query = select(Reference).where(Reference.id == reference_id)
    reference: Reference = (await async_session.execute(query)).scalar()
    assert reference.issue.id == issue_id
    assert reference.issue.journal.id == journal_id
    assert reference.issue.journal.titles == ["Fake scientific journal"]
    assert reference.issue.journal.issn == "1234-5678"
    assert reference.issue.volume == "1"
    assert reference.issue.number == ["1"]
    assert reference.issue.date == "2021"
    assert reference.titles[0].value == "Fake scientific article"
    assert reference.titles[0].language == "en"
    assert reference.custom_metadata is None
    await async_session.delete(reference)


async def test_issue_is_deleted_when_journal_is_deleted(async_session: AsyncSession):
    """
    GIVEN a reference with an issue and a journal
    WHEN the journal is deleted
    THEN the issue is deleted and the reference
    still exists but does not belong to the issue anymore
    """
    journal = Journal(
        source="source",
        source_identifier="source_identifier_1234",
        titles=["Fake scientific journal"],
        issn="1234-5678",
    )
    issue = Issue(
        source="source",
        source_identifier="source_identifier_1234",
        volume="1",
        number=["1"],
        journal=journal,
    )
    reference = Reference(
        source_identifier="source_identifier_1234",
        harvester="harvester",
        hash="hash",
        version=0,
        titles=[Title(value="Fake scientific article", language="en")],
        issue=issue,
    )
    async_session.add(reference)
    await async_session.commit()
    journal_id = journal.id
    issue_id = issue.id
    reference_id = reference.id
    await async_session.delete(journal)
    await async_session.commit()
    async_session.expire(reference)
    # the journal and the issue are deleted
    query = select(Journal).where(Journal.id == journal_id)
    journal: Journal = (await async_session.execute(query)).scalar()
    assert journal is None
    query = select(Issue).where(Issue.id == issue_id)
    issue: Issue = (await async_session.execute(query)).scalar()
    assert issue is None
    # the reference does not belong to the issue anymore
    query = (
        select(Reference)
        .options(joinedload(Reference.issue))
        .where(Reference.id == reference_id)
    )
    reference: Reference = (await async_session.execute(query)).scalar()
    assert reference.issue is None
    assert reference.custom_metadata is None


async def test_reference_is_not_deleted_when_issue_is_deleted(
    async_session: AsyncSession,
):
    """
    GIVEN a reference with an issue and a journal
    WHEN the issue is deleted
    THEN the reference still exists but does
    not belong to the issue anymore
    """
    journal = Journal(
        source="source",
        source_identifier="source_identifier_1234",
        titles=["Fake scientific journal"],
        issn="1234-5678",
    )
    issue = Issue(
        source="source",
        source_identifier="source_identifier_1234",
        volume="1",
        number=["1"],
        journal=journal,
    )
    reference = Reference(
        source_identifier="source_identifier_1234",
        harvester="harvester",
        hash="hash",
        version=0,
        titles=[Title(value="Fake scientific article", language="en")],
        issue=issue,
    )
    async_session.add(reference)
    await async_session.commit()
    issue_id = issue.id
    reference_id = reference.id
    journal_id = journal.id
    await async_session.delete(issue)
    await async_session.commit()
    async_session.expire_all()
    # the issue is deleted
    query = select(Issue).where(Issue.id == issue_id)
    issue: Issue = (await async_session.execute(query)).scalar()
    assert issue is None
    # the reference does not belong to the issue anymore
    query = (
        select(Reference)
        .options(joinedload(Reference.issue))
        .where(Reference.id == reference_id)
    )
    reference: Reference = (await async_session.execute(query)).scalar()
    assert reference is not None
    assert reference.issue is None
    assert reference.custom_metadata is None
    # the journal still exists
    query = select(Journal).where(Journal.id == journal_id)
    journal: Journal = (await async_session.execute(query)).scalar()
    assert journal is not None


async def test_journal_and_issue_not_deleted_when_reference_deleted(
    async_session: AsyncSession,
):
    """
    GIVEN a reference with an issue and a journal
    WHEN the reference is deleted
    THEN the journal and the issue still exist
    """
    journal = Journal(
        source="source",
        source_identifier="source_identifier_1234",
        titles=["Fake scientific journal"],
        issn=["1234-5678"],
        eissn=["5678-1234"],
        issn_l="1111-2222",
    )
    issue = Issue(
        source="source",
        source_identifier="source_identifier_1234",
        volume="1",
        number=["1"],
        journal=journal,
    )
    reference = Reference(
        source_identifier="source_identifier_1234",
        harvester="harvester",
        hash="hash",
        version=0,
        titles=[Title(value="Fake scientific article", language="en")],
        issue=issue,
    )
    async_session.add(reference)
    await async_session.commit()
    journal_id = journal.id
    issue_id = issue.id
    reference_id = reference.id
    await async_session.delete(reference)
    await async_session.commit()
    async_session.expire_all()
    # the reference is deleted
    query = select(Reference).where(Reference.id == reference_id)
    reference: Reference = (await async_session.execute(query)).scalar()
    assert reference is None
    # the journal still exists
    query = select(Journal).where(Journal.id == journal_id)
    journal: Journal = (await async_session.execute(query)).scalar()
    assert journal is not None
    # the issue still exists
    query = select(Issue).options(joinedload(Issue.journal)).where(Issue.id == issue_id)
    issue: Issue = (await async_session.execute(query)).scalar()
    assert issue is not None
    assert issue.journal is not None
    assert issue.journal.id == journal_id
    assert issue.journal.titles == ["Fake scientific journal"]
    assert "1234-5678" in issue.journal.issn
    assert "5678-1234" in issue.journal.eissn
    assert issue.journal.issn_l == "1111-2222"
    assert issue.volume == "1"
    assert issue.number == ["1"]
    await async_session.delete(issue)
    await async_session.delete(journal)
    await async_session.commit()


async def test_reference_with_collection_codes(async_session: AsyncSession):
    """
    GIVEN a reference with a collection code
    WHEN the reference is created
    THEN check the reference has the correct attributes
    """
    reference = Reference(
        source_identifier="source_identifier_1234",
        harvester="hal",
        hash="hash",
        version=0,
        titles=[Title(value="Fake scientific article", language="en")],
        custom_metadata=HalCustomMetadataSchema(
            hal_collection_codes=[
                "SHS",
                "UNIV-PARIS7",
                "UPMC",
                "UNIV-LYON1",
                "UNIV-PSUD",
                "UNIV-STRASBG1",
                "INRA",
                "IFR69",
                "UNIV-STRASBG",
                "UNIV-PARIS-SACLAY",
            ],
            hal_submit_type=HalCustomMetadataSchema.HalSubmitType.NOTICE,
        ).model_dump(),
    )
    async_session.add(reference)
    await async_session.commit()
    reference_id = reference.id
    query = select(Reference).where(Reference.id == reference_id)
    reference: Reference = (await async_session.execute(query)).scalar()
    assert reference.custom_metadata["hal_collection_codes"] == [
        "SHS",
        "UNIV-PARIS7",
        "UPMC",
        "UNIV-LYON1",
        "UNIV-PSUD",
        "UNIV-STRASBG1",
        "INRA",
        "IFR69",
        "UNIV-STRASBG",
        "UNIV-PARIS-SACLAY",
    ]
    assert reference.custom_metadata["hal_submit_type"] == "notice"


@pytest.mark.asyncio
async def test_reference_with_valid_hal_submit_type(async_session):
    """
    GIVEN a reference with a valid hal_submit_type
    WHEN the reference is created
    THEN the value is stored and retrieved correctly
    """
    reference = Reference(
        source_identifier="source_identifier_valid_type",
        harvester="hal",
        hash="abc123",
        version=1,
        titles=[Title(value="With HAL submit type", language="en")],
        custom_metadata=HalCustomMetadataSchema(
            hal_collection_codes=[],
            hal_submit_type=HalCustomMetadataSchema.HalSubmitType.FILE.value,
        ).model_dump(),
    )
    async_session.add(reference)
    await async_session.commit()
    reference_id = reference.id

    query = select(Reference).where(Reference.id == reference_id)
    reference: Reference = (await async_session.execute(query)).unique().scalar()
    assert reference.custom_metadata["hal_submit_type"] == "file"


@pytest.mark.asyncio
async def test_reference_with_invalid_hal_submit_type_raises():
    """
    GIVEN a reference with an invalid hal_submit_type
    WHEN it is added to the session
    THEN a ValueError is raised at validation time
    """
    with pytest.raises(ValueError, match="Input should be 'notice', 'file' or 'annex'"):
        Reference(
            source_identifier="source_identifier_invalid_type",
            harvester="hal",
            hash="xyz456",
            version=1,
            titles=[Title(value="Invalid HAL submit type", language="en")],
            custom_metadata=HalCustomMetadataSchema(
                hal_collection_codes=[],
                hal_submit_type="invalid_type",
            ).model_dump(),
        )
