"""
Test the validate_reference decorator of the AbstractReferencesConverter class.
"""
import pytest

from app.db.models.reference import Reference as DbReference
from app.db.models.title import Title as DbTitle
from app.harvesters.abstract_references_converter import AbstractReferencesConverter


@pytest.fixture(name="reference_without_title")
def fixture_reference_without_title():
    return DbReference(
        source_identifier="I am unique !",
        titles=[],
    )


@pytest.fixture(name="reference_without_identifier")
def fixture_reference_without_identifier():
    return DbReference(
        titles=[DbTitle(value="I am a title")],
    )


@pytest.fixture(name="reference_with_title_and_identifier")
def fixture_reference_with_title_and_identifier():
    return DbReference(
        source_identifier="I am unique !",
        titles=[DbTitle(value="I am a title")],
    )


@pytest.mark.asyncio
@pytest.mark.current
async def test_reference_without_title_raises_exception(reference_without_title):
    """
    Given a reference without title
    When the validate_reference decorator is called
    Then an AssertionError should be raised

    :param reference_without_title: A reference without title
    """

    async def decorated_function(self):
        return reference_without_title

    function_with_decorator = AbstractReferencesConverter.validate_reference(
        decorated_function
    )
    with pytest.raises(AssertionError) as exc_info:
        await function_with_decorator(AbstractReferencesConverter)

    assert exc_info.match("titles should be set on reference")


@pytest.mark.asyncio
@pytest.mark.current
async def test_reference_without_identifier_raises_exception(
    reference_without_identifier,
):
    """ "
    Given a reference without identifier
    When the validate_reference decorator is called
    Then an AssertionError should be raised

    :param reference_without_identifier: A reference without identifier
    """

    async def decorated_function(self):
        return reference_without_identifier

    function_with_decorator = AbstractReferencesConverter.validate_reference(
        decorated_function
    )
    with pytest.raises(AssertionError) as exc_info:
        await function_with_decorator(AbstractReferencesConverter)

    assert exc_info.match("Source identifier should be set on reference")


@pytest.mark.asyncio
@pytest.mark.current
async def test_reference_with_title_and_identifier_does_not_raise_exception(
    reference_with_title_and_identifier,
):
    """
    Given a reference with title and identifier
    When the validate_reference decorator is called
    Then the reference should be returned

    :param reference_with_title_and_identifier:
    """

    async def decorated_function(self):
        return reference_with_title_and_identifier

    function_with_decorator = AbstractReferencesConverter.validate_reference(
        decorated_function
    )
    result = await function_with_decorator(AbstractReferencesConverter)

    assert result == reference_with_title_and_identifier
