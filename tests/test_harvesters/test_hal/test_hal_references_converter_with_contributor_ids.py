import pytest
from semver import VersionInfo

from app.db.daos.contributor_dao import ContributorDAO
from app.db.models.contributor_identifier import ContributorIdentifier
from app.db.session import async_session
from app.harvesters.hal.hal_harvester import HalHarvester
from app.harvesters.hal.hal_references_converter import HalReferencesConverter
from app.harvesters.json_harvester_raw_result import JsonHarvesterRawResult


@pytest.fixture(name="hal_api_docs_with_contributor_identifiers_content")
def fixture_hal_api_docs_with_contributor_identifiers_content(
    hal_api_docs_with_contributor_identifiers,
):
    """Return the list of document references from hal response"""
    return hal_api_docs_with_contributor_identifiers["response"]["docs"]


async def test_convert(
    hal_api_docs_with_contributor_identifiers_content,
):  # pylint: disable=too-many-locals
    """Test that the converter will return normalised references"""
    converter_under_tests = HalReferencesConverter(name="hal")

    doc_0 = hal_api_docs_with_contributor_identifiers_content[0]
    result = JsonHarvesterRawResult(
        source_identifier=doc_0["docid"],
        payload=doc_0,
        formatter_name=HalHarvester.FORMATTER_NAME,
    )
    test_reference = converter_under_tests.build(
        raw_data=result, harvester_version=VersionInfo.parse("0.0.0")
    )
    await converter_under_tests.convert(raw_data=result, new_ref=test_reference)
    contribution = test_reference.contributions[0]
    contributor_id = contribution.contributor.id
    assert contributor_id is not None
    assert isinstance(contributor_id, int)
    async with async_session() as session:
        async with session.begin_nested():
            contributor = await ContributorDAO(session).get_by_id(contributor_id)
            assert contributor is not None
            assert contributor.name == "Vincent Bichet"
            assert contributor.first_name == "Vincent"
            assert contributor.last_name == "Bichet"
            assert len(contributor.identifiers) == 6
            assert any(
                identifier.type == ContributorIdentifier.IdentifierType.ORCID.value
                and identifier.value == "0000-0002-3053-9512"
                for identifier in contributor.identifiers
            )
            assert any(
                identifier.type == ContributorIdentifier.IdentifierType.ISNI.value
                and identifier.value == "0000000071437032"
                for identifier in contributor.identifiers
            )
            assert any(
                identifier.type
                == ContributorIdentifier.IdentifierType.GOOGLE_SCHOLAR.value
                and identifier.value == "_88eIccAAAAJ"
                for identifier in contributor.identifiers
            )
            assert any(
                identifier.type == ContributorIdentifier.IdentifierType.IDHAL_I.value
                and identifier.value == "1288873"
                for identifier in contributor.identifiers
            )
            assert any(
                identifier.type == ContributorIdentifier.IdentifierType.IDREF.value
                and identifier.value == "121561712"
                for identifier in contributor.identifiers
            )
            assert any(
                identifier.type == ContributorIdentifier.IdentifierType.VIAF.value
                and identifier.value == "56924466"
                for identifier in contributor.identifiers
            )
