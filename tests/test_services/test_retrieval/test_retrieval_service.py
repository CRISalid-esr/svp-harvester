"""Test the references API."""

from app.config import get_app_settings
from app.harvesters.hal.hal_harvester import HalHarvester
from app.harvesters.idref.idref_harvester import IdrefHarvester
from app.harvesters.scanr.scanr_harvester import ScanrHarvester
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
