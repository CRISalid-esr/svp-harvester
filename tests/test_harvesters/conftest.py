from unittest import mock

import pytest

from app.db.references.references_recorder import ReferencesRecorder


@pytest.fixture(name="reference_recorder_register_mock")
def fixture_reference_recorder_register_mock():
    """Reference recorder mock to detect register method calls."""
    with mock.patch.object(
            ReferencesRecorder, "register_creation"
    ) as reference_recorder_register_mock:
        yield reference_recorder_register_mock
