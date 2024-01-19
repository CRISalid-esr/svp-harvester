from unittest import mock
from loguru import logger

import pytest
from pytest import LogCaptureFixture

from app.db.references.references_recorder import ReferencesRecorder


@pytest.fixture(name="reference_recorder_register_mock")
def fixture_reference_recorder_register_mock():
    """Reference recorder mock to detect register method calls."""
    with mock.patch.object(
        ReferencesRecorder, "register_creation"
    ) as reference_recorder_register_mock:
        yield reference_recorder_register_mock


@pytest.fixture(autouse=True)
def caplog(caplog: LogCaptureFixture):  # pylint: disable=redefined-outer-name
    """
    Make pytest work with loguru. See:
    https://loguru.readthedocs.io/en/stable/resources/migration.html#making-things-work-with-pytest-and-caplog
    :param caplog: pytest fixture
    :return: loguru compatible caplog
    """
    handler_id = logger.add(
        caplog.handler,
        format="{message}",
        level=0,
        filter=lambda record: record["level"].no >= caplog.handler.level,
        enqueue=False,
    )
    yield caplog
    try:
        logger.remove(handler_id)
    except ValueError:
        pass
