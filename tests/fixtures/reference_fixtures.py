import isodate
import pytest_asyncio

from app.db.models.concept import Concept as DbConcept
from app.db.models.label import Label
from app.db.models.reference import Reference as DbReference
from app.db.models.subtitle import Subtitle
from app.db.models.title import Title


@pytest_asyncio.fixture(name="reference_db_model")
async def fixture_reference_db_model() -> DbReference:
    """
    Create a reference db model
    :return: reference db model
    """
    reference = DbReference(
        source_identifier="123456789",
        harvester="hal",
        hash="hash1",
        version=0,
        titles=[Title(value="title", language="fr")],
        subtitles=[Subtitle(value="subtitle", language="fr")],
        issued=isodate.parse_datetime("2017-01-01T00:00:00"),
        created=isodate.parse_datetime("2018-02-02T10:00:00"),
    )
    reference.subjects.append(
        DbConcept(
            uri="http://uri",
            labels=[Label(value="label", language="fr")],
        )
    )
    return reference
