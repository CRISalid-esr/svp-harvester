"""
Tests for the namespaced HAL contributor identifiers (issue #910).

HAL author-form ids and numeric idHals are independent numeric namespaces:
without prefixes, a contributor whose idHal is N and a contributor whose
form id is N (no idHal) would collide into a single Contributor row.
"""

from unittest import mock

import pytest
from semver import VersionInfo

from app.db.models.organization import Organization as DbOrganization
from app.harvesters.exceptions.unexpected_format_exception import (
    UnexpectedFormatException,
)
from app.harvesters.hal.hal_harvester import HalHarvester
from app.harvesters.hal.hal_references_converter import HalReferencesConverter
from app.harvesters.json_harvester_raw_result import JsonHarvesterRawResult
from app.services.organizations.hal_organization_solver import HalOrganizationSolver


@pytest.fixture(name="echo_hal_organization_solver")
def fixture_echo_hal_organization_solver():
    """
    Override the global fake HAL organization solver with one that echoes
    the requested identifier and name, so that affiliations can be told apart.
    """

    async def echo_solver(organization_information):
        return DbOrganization(
            source="hal",
            source_identifier=organization_information.identifier,
            name=organization_information.name,
            type="laboratory",
        )

    with mock.patch.object(
        HalOrganizationSolver, "solve", side_effect=echo_solver
    ) as mock_solve:
        yield mock_solve


async def _converted_reference(doc: dict):
    converter = HalReferencesConverter(name="hal")
    result = JsonHarvesterRawResult(
        source_identifier=doc["docid"],
        payload=doc,
        formatter_name=HalHarvester.FORMATTER_NAME,
    )
    reference = converter.build(
        raw_data=result, harvester_version=VersionInfo.parse("0.0.0")
    )
    await converter.convert(raw_data=result, new_ref=reference)
    return reference


async def test_colliding_numeric_ids_yield_distinct_contributors(
    hal_api_docs_with_ambiguous_contributor_ids,
    echo_hal_organization_solver,  # pylint: disable=unused-argument
):
    """
    A contributor with idHal 12345 and a contributor with form id 12345
    (no idHal) must produce two distinct contributors with namespaced
    identifiers, not a single merged one.
    """
    doc = hal_api_docs_with_ambiguous_contributor_ids["response"]["docs"][0]
    reference = await _converted_reference(doc)

    assert len(reference.contributions) == 2
    contributors_by_name = {
        contribution.contributor.name: contribution.contributor
        for contribution in reference.contributions
    }
    assert contributors_by_name["Alice Idhal"].source_identifier == "idhal:12345"
    assert contributors_by_name["Bob Form"].source_identifier == "form:12345"
    assert contributors_by_name["Alice Idhal"].id != contributors_by_name["Bob Form"].id


async def test_affiliations_are_matched_per_namespace(
    hal_api_docs_with_ambiguous_contributor_ids,
    echo_hal_organization_solver,  # pylint: disable=unused-argument
):
    """
    Affiliations from authIdHasPrimaryStructure_fs must be matched on the
    right namespace: by idHal when the contributor has one, by form id
    otherwise (the form id case never matched before issue #910).
    """
    doc = hal_api_docs_with_ambiguous_contributor_ids["response"]["docs"][0]
    reference = await _converted_reference(doc)

    affiliations_by_name = {
        contribution.contributor.name: [
            affiliation.name for affiliation in contribution.affiliations
        ]
        for contribution in reference.contributions
    }
    assert affiliations_by_name["Alice Idhal"] == ["Org Alpha"]
    assert affiliations_by_name["Bob Form"] == ["Org Beta"]


async def test_malformed_contributor_ids_raise_unexpected_format(
    hal_api_docs_with_ambiguous_contributor_ids,
):
    """
    An ids segment that does not split into exactly formId-idHal must raise
    an UnexpectedFormatException instead of a bare ValueError.
    """
    doc = hal_api_docs_with_ambiguous_contributor_ids["response"]["docs"][0]
    doc["authFullNameFormIDPersonIDIDHal_fs"][
        0
    ] = "Alice Idhal_FacetSep_111-12345-0_FacetSep_alice-idhal"
    with pytest.raises(UnexpectedFormatException, match="Unexpected contributor ids"):
        await _converted_reference(doc)
