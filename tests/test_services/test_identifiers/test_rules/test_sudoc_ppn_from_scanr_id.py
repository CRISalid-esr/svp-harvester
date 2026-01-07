import pytest

from app.db.models.reference import Reference
from app.db.models.reference_identifier import ReferenceIdentifier
from app.services.identifiers.identifier_inference_service import (
    IdentifierInferenceService,
)


def test_infer_sudoc_ppn_from_scanr_id_adds_identifier():
    """
    Test that the sudoc-ppn identifier is correctly inferred from the ScanR source_identifier
    :return:
    """
    ref = Reference(source_identifier="sudoc258403519")
    ref.identifiers = []

    IdentifierInferenceService.infer_identifiers(
        reference=ref,
        rules=[IdentifierInferenceService.Rule.SUDOC_PPN_FROM_SCANR_ID],
    )

    assert any(
        i.type == "sudoc-ppn" and i.value == "258403519" for i in ref.identifiers
    )


def test_infer_sudoc_ppn_from_scanr_id_does_nothing_if_already_present():
    """
    Test that no duplicate sudoc-ppn identifier is added if one is already present
    :return:
    """
    ref = Reference(source_identifier="sudoc258403519")
    ref.identifiers = [ReferenceIdentifier(type="sudoc-ppn", value="258403519")]

    IdentifierInferenceService.infer_identifiers(
        reference=ref,
        rules=[IdentifierInferenceService.Rule.SUDOC_PPN_FROM_SCANR_ID],
    )

    assert len([i for i in ref.identifiers if i.type == "sudoc-ppn"]) == 1


@pytest.mark.parametrize("sid", ["scanr123", "sudocABC", "sudoc-123", "", None])
def test_infer_sudoc_ppn_from_scanr_id_ignores_non_matching_source_identifier(sid):
    """
    Test that no sudoc-ppn identifier is added for non-matching ScanR source_identifiers
    :param sid:
    :return:
    """
    ref = Reference(source_identifier=sid)
    ref.identifiers = []

    IdentifierInferenceService.infer_identifiers(
        reference=ref,
        rules=[IdentifierInferenceService.Rule.SUDOC_PPN_FROM_SCANR_ID],
    )

    assert not any(i.type == "sudoc-ppn" for i in ref.identifiers)
