import pytest
from semver import VersionInfo

from app.db.daos.contributor_dao import ContributorDAO
from app.db.models.contributor_identifier import ContributorIdentifier
from app.db.session import async_session
from app.harvesters.json_harvester_raw_result import JsonHarvesterRawResult
from app.harvesters.scanr.scanr_harvester import ScanrHarvester
from app.harvesters.scanr.scanr_references_converter import ScanrReferencesConverter


@pytest.fixture(name="scanr_publication_doc_with_journal_with_title")
def fixture_scanr_publication_doc_with_journal_with_title(
    scanr_publication_doc_with_journal_with_title,
):
    """Return the list of dictionaries references from scanr response"""
    return scanr_publication_doc_with_journal_with_title["hits"]["hits"]


@pytest.fixture(name="scanr_publication_doc_with_anon_author")
def fixture_scanr_publication_doc_with_anon_author(
    scanr_publication_doc_with_anon_author,
):
    """Return list of dict references from scanr response"""
    return scanr_publication_doc_with_anon_author["hits"]["hits"]


async def test_convert_publication_with_contributor_ids(
    scanr_publication_doc_with_journal_with_title,
):
    """
    Test that the converter will persist contributor identifiers correctly
    :param scanr_publication_doc_with_journal_with_title:
    :return:
    """
    converter_under_tests = ScanrReferencesConverter(name="scanr")

    doc = scanr_publication_doc_with_journal_with_title[0]
    result = JsonHarvesterRawResult(
        source_identifier=doc.get("_id"),
        payload=doc,
        formatter_name=ScanrHarvester.FORMATTER_NAME,
    )

    test_reference = converter_under_tests.build(
        raw_data=result, harvester_version=VersionInfo.parse("0.0.0")
    )
    await converter_under_tests.convert(raw_data=result, new_ref=test_reference)

    # take contribution of rank 1
    contribution = next(c for c in test_reference.contributions if c.rank == 1)
    contributor_id = contribution.contributor.id
    assert contributor_id is not None
    assert isinstance(contributor_id, int)
    async with async_session() as session:
        async with session.begin_nested():
            contributor = await ContributorDAO(session).get_by_id(contributor_id)
            assert contributor is not None
            assert contributor.name == "Valentine Roux"
            assert contributor.first_name == "Valentine"
            assert contributor.last_name == "Roux"
            assert len(contributor.identifiers) == 3
            assert any(
                identifier.type == ContributorIdentifier.IdentifierType.ORCID
                and identifier.value == "0000-0002-9981-9598"
                for identifier in contributor.identifiers
            )
            assert any(
                identifier.type == ContributorIdentifier.IdentifierType.IDREF
                and identifier.value == "028738497"
                for identifier in contributor.identifiers
            )
            assert any(
                identifier.type == ContributorIdentifier.IdentifierType.IDHAL_S
                and identifier.value == "valentine-roux"
                for identifier in contributor.identifiers
            )


async def test_convert_publication_with_anon_contributor_id(
    scanr_publication_doc_with_anon_author,
):
    """
    Test that the converter will generate an anon contributor identifier correctly
    :param scanr_publication_doc_with_anon_author:
    :return:
    """
    converter_under_tests = ScanrReferencesConverter(name="scanr")

    doc = scanr_publication_doc_with_anon_author[0]
    result = JsonHarvesterRawResult(
        source_identifier=doc.get("_id"),
        payload=doc,
        formatter_name=ScanrHarvester.FORMATTER_NAME,
    )

    test_reference = converter_under_tests.build(
        raw_data=result, harvester_version=VersionInfo.parse("0.0.0")
    )
    await converter_under_tests.convert(raw_data=result, new_ref=test_reference)

    # rank 0 = anon author (no "person" / no "toIdentify")
    contribution = next(c for c in test_reference.contributions if c.rank == 0)
    contributor_id = contribution.contributor.id

    assert contributor_id is not None
    assert isinstance(contributor_id, int)

    async with async_session() as session:
        async with session.begin_nested():
            contributor = await ContributorDAO(session).get_by_id(contributor_id)
            assert contributor is not None

            # contributor details
            assert contributor.name == "Panel Lindor"
            assert contributor.first_name == "Panel"
            assert contributor.last_name == "Lindor"

            # critical: the synthetic source identifier is persisted (no NULL)
            expected_source_id = f"anon:{doc.get('_id')}:panel-lindor"
            assert contributor.source_identifier == expected_source_id

            # no denormalized identifiers for this author
            assert len(contributor.identifiers) == 0
