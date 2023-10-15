"""Test the references API."""
import pytest

from app.config import get_app_settings
from app.db.models.retrieval import Retrieval
from app.harvesters.hal.hal_harvester import HalHarvester
from app.harvesters.idref.idref_harvester import IdrefHarvester
from app.harvesters.scanr.scanr_harvester import ScanrHarvester
from app.models.people import Person
from app.services.retrieval.retrieval_service import RetrievalService


def test_retrieval_service_build_harvesters():
    """Test that the retrieval service builds the expected harvesters from the yml settings."""
    settings = get_app_settings()
    service = RetrievalService(settings)
    service._build_harvesters()  # pylint: disable=protected-access
    assert len(service.harvesters) == 3
    assert "hal" in service.harvesters
    assert "idref" in service.harvesters
    assert "scanr" in service.harvesters
    assert isinstance(service.harvesters["hal"], HalHarvester)
    assert isinstance(service.harvesters["idref"], IdrefHarvester)
    assert isinstance(service.harvesters["scanr"], ScanrHarvester)


@pytest.mark.asyncio
async def test_retrieval_service_returns_retrieval_for_person(
    person_with_name_and_idref: Person,
):
    """
    GIVEN a retrieval service
    WHEN registering a person
    THEN a retrieval is returned with the person as entity

    :param person_with_name_and_idref:
    :return:
    """
    settings = get_app_settings()
    service = RetrievalService(settings)
    retrieval: Retrieval = await service.register(person_with_name_and_idref)
    assert retrieval.entity.name == person_with_name_and_idref.name
    assert retrieval.entity.get_identifier(
        "idref"
    ) == person_with_name_and_idref.get_identifier("idref")
