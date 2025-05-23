# file: tests/models/test_custom_metadata_validation.py

import pytest

from app.db.models.reference import Reference as DbReference
from app.harvesters.hal.hal_custom_metadata_schema import HalCustomMetadataSchema


@pytest.fixture(autouse=True)
def clear_registry():
    """
    Cancel the automatic registration of the custom metadata schema
    :return:
    """
    DbReference.custom_metadata_schema_registry.clear()
    yield
    DbReference.custom_metadata_schema_registry.clear()


def test_custom_metadata_validation_passes_when_schema_registered():
    DbReference.register_custom_metadata_schema("HAL", HalCustomMetadataSchema)

    ref = DbReference(
        source_identifier="123",
        harvester="HAL",
        version=0,
        hash="abc",
        harvester_version="1.0.0",
        custom_metadata={"hal_submit_type": "notice", "hal_collection_codes": ["ABC"]},
    )

    assert ref.custom_metadata["hal_submit_type"] == "notice"
    assert ref.custom_metadata["hal_collection_codes"] == ["ABC"]


def test_custom_metadata_validation_fails_when_no_schema_registered():
    with pytest.raises(ValueError) as exc_info:
        DbReference(
            source_identifier="123",
            harvester="hal",
            version=0,
            hash="abc",
            harvester_version="1.0.0",
            custom_metadata={
                "hal_submit_type": "notice",
                "hal_collection_codes": ["ABC"],
            },
        )
    assert "No schema registered for hal harvester" in str(exc_info.value)
