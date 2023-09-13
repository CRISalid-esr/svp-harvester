"""Test the references API."""
from os import environ

from app.config import get_app_settings
from app.harvesters.idref.idref_harvester import IdrefHarvester
from app.harvesters.scanr.scanr_harvester import ScanrHarvester
from app.services.retrieval.retrieval_service import RetrievalService


def test_retrieval_service_build_harvesters():
    settings = get_app_settings()
    service = RetrievalService(settings)
    service._build_harvesters()
    assert len(service.harvesters) == 2
    assert "idref" in service.harvesters
    assert "scanr" in service.harvesters
    assert type(service.harvesters["idref"]) == IdrefHarvester
    assert type(service.harvesters["scanr"]) == ScanrHarvester
