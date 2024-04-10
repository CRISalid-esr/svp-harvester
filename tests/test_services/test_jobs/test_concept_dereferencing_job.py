import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.concept import Concept
from app.services.concepts.unknown_authority_exception import UnknownAuthorityException
from app.services.jobs.concept_dereferencing_job import ConceptDereferencingJob


@pytest.mark.asyncio
async def test_dereference_job(async_session: AsyncSession):
    """
    Test that the dereferencing job can dereference a concept.
    """
    concept = Concept(uri="http://www.idref.fr/123456789X/id", dereferenced=False)
    async_session.add(concept)
    await async_session.commit()

    job = ConceptDereferencingJob()
    await job.run()

    await async_session.refresh(concept)

    assert concept.dereferenced is True
    assert concept.labels[0].value == "Idref concept allowed for test"


@pytest.mark.asyncio
async def test_derefence_job_unknown_id(async_session: AsyncSession):
    """
    Test that is the concept id is unknown, an exception is raised.
    """
    concept = Concept(uri="http://example.com/concept", dereferenced=False)
    async_session.add(concept)
    await async_session.commit()

    job = ConceptDereferencingJob()
    with pytest.raises(UnknownAuthorityException):
        await job.run()
