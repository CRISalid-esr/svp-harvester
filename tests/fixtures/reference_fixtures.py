import pytest_asyncio

from app.db.models.reference import Reference as DbReference
from app.db.models.title import Title


@pytest_asyncio.fixture(name="reference_db_model")
async def fixture_reference_db_model() -> DbReference:
    """
    Create a reference db model
    :return: reference db model
    """
    return DbReference(
        source_identifier="123456789",
        harvester="hal",
        hash="hash1",
        version=0,
        titles=[Title(value="title", language="fr")],
    )
