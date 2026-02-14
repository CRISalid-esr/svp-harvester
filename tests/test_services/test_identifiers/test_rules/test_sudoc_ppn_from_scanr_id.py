import pytest

from app.db.models.reference import Reference
from app.db.models.reference_identifier import ReferenceIdentifier
from app.services.identifiers.identifier_inference_service import (
    IdentifierInferenceService,
)


def _infer(ref: Reference) -> None:
    IdentifierInferenceService.infer_identifiers(
        reference=ref,
        rules=[IdentifierInferenceService.Rule.SUDOC_PPN_FROM_SCANR_ID],
    )


def test_infer_sudoc_ppn_from_scanr_id_adds_identifier():
    """
    Test that the ppn identifier is correctly inferred from the ScanR source_identifier
    """
    ref = Reference(source_identifier="sudoc258403519")
    ref.identifiers = []

    _infer(ref)

    assert any(i.type == "ppn" and i.value == "258403519" for i in ref.identifiers)


def test_infer_sudoc_ppn_from_scanr_id_adds_identifier_with_trailing_X():
    """
    PPN may end with a trailing check character X
    """
    ref = Reference(source_identifier="sudoc12345678X")
    ref.identifiers = []

    _infer(ref)

    assert any(i.type == "ppn" and i.value == "12345678X" for i in ref.identifiers)


def test_infer_sudoc_ppn_from_scanr_id_normalizes_trailing_x_to_uppercase():
    """
    Lowercase x should be normalized to uppercase X
    """
    ref = Reference(source_identifier="sudoc12345678x")
    ref.identifiers = []

    _infer(ref)

    assert any(i.type == "ppn" and i.value == "12345678X" for i in ref.identifiers)


def test_infer_sudoc_ppn_from_scanr_id_strips_whitespace():
    """
    Leading/trailing whitespace in source_identifier should be ignored
    """
    ref = Reference(source_identifier="  sudoc258403519  ")
    ref.identifiers = []

    _infer(ref)

    assert any(i.type == "ppn" and i.value == "258403519" for i in ref.identifiers)


def test_infer_sudoc_ppn_from_scanr_id_is_case_insensitive_for_prefix():
    """
    'sudoc' prefix may come in different cases
    """
    ref = Reference(source_identifier="SUDOC258403519")
    ref.identifiers = []

    _infer(ref)

    assert any(i.type == "ppn" and i.value == "258403519" for i in ref.identifiers)


def test_infer_sudoc_ppn_from_scanr_id_does_nothing_if_already_present():
    """
    Test that no duplicate ppn identifier is added if one is already present
    """
    ref = Reference(source_identifier="sudoc258403519")
    ref.identifiers = [ReferenceIdentifier(type="ppn", value="258403519")]

    _infer(ref)

    assert len([i for i in ref.identifiers if i.type == "ppn"]) == 1


@pytest.mark.parametrize(
    "sid",
    [
        "scanr123",
        "sudocABC",  # letters not allowed (except trailing X)
        "sudoc-123",  # hyphen not allowed
        "sudoc123X456",  # X not allowed in the middle
        "sudocX",  # no digits
        "sudoc123xx",  # only one trailing X allowed
        "",  # empty string
        None,  # None
    ],
)
def test_infer_sudoc_ppn_from_scanr_id_ignores_non_matching_source_identifier(sid):
    """
    Test that no ppn identifier is added for non-matching ScanR source_identifiers
    """
    ref = Reference(source_identifier=sid)
    ref.identifiers = []

    _infer(ref)

    assert not any(i.type == "ppn" for i in ref.identifiers)
