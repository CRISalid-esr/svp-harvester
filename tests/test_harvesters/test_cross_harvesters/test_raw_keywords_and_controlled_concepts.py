import pytest
from semver import VersionInfo
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.models.concept import Concept
from app.db.models.label import Label
from app.db.session import async_session
from app.harvesters.hal.hal_harvester import HalHarvester
from app.harvesters.hal.hal_references_converter import HalReferencesConverter
from app.harvesters.json_harvester_raw_result import JsonHarvesterRawResult
from app.harvesters.open_alex.open_alex_harvester import OpenAlexHarvester
from app.harvesters.open_alex.open_alex_references_converter import (
    OpenAlexReferencesConverter,
)


@pytest.fixture(name="hal_api_docs_collision_cleaned_response")
def fixture_hal_api_docs_collision_cleaned_response(
    hal_api_docs_with_keyword_collision_controlled_concept,
):
    return hal_api_docs_with_keyword_collision_controlled_concept["response"]["docs"]


@pytest.mark.asyncio
async def test_raw_keywords_and_controlled_concepts_stay_separated(
    open_alex_api_work: dict,
    hal_api_docs_collision_cleaned_response: list[dict],
):
    open_alex_converter = OpenAlexReferencesConverter(name="openalex")
    hal_converter = HalReferencesConverter(name="hal")

    open_alex_result = JsonHarvesterRawResult(
        source_identifier=open_alex_api_work["id"],
        payload=open_alex_api_work,
        formatter_name=OpenAlexHarvester.FORMATTER_NAME,
    )
    open_alex_reference = open_alex_converter.build(
        raw_data=open_alex_result,
        harvester_version=VersionInfo.parse("0.0.0"),
    )
    await open_alex_converter.convert(
        raw_data=open_alex_result,
        new_ref=open_alex_reference,
    )

    assert len(open_alex_reference.subjects) == 1
    open_alex_concept = open_alex_reference.subjects[0]
    assert open_alex_concept.uri is not None
    assert any(label.value == "Test concept" for label in open_alex_concept.labels)

    hal_doc = hal_api_docs_collision_cleaned_response[0]
    hal_result = JsonHarvesterRawResult(
        source_identifier=hal_doc["docid"],
        payload=hal_doc,
        formatter_name=HalHarvester.FORMATTER_NAME,
    )
    hal_reference = hal_converter.build(
        raw_data=hal_result,
        harvester_version=VersionInfo.parse("0.0.0"),
    )
    await hal_converter.convert(
        raw_data=hal_result,
        new_ref=hal_reference,
    )

    assert len(hal_reference.subjects) == 1
    hal_keyword_concept = hal_reference.subjects[0]

    assert hal_keyword_concept.id != open_alex_concept.id
    assert hal_keyword_concept.uri is None
    assert open_alex_concept.uri is not None
    assert len(hal_keyword_concept.labels) == 1
    assert hal_keyword_concept.labels[0].value == "Test concept"
    assert hal_keyword_concept.labels[0].language == "en"

    async with async_session() as session:
        stmt = (
            select(Concept)
            .options(selectinload(Concept.labels))
            .join(Concept.labels)
            .where(
                Label.value == "Test concept",
                Label.language == "en",
            )
            .distinct()
        )
        concepts = (await session.execute(stmt)).scalars().unique().all()

    assert len(concepts) == 2
    assert len([concept for concept in concepts if concept.uri is None]) == 1
    assert len([concept for concept in concepts if concept.uri is not None]) == 1

    raw_keyword = next(concept for concept in concepts if concept.uri is None)
    controlled_concept = next(
        concept for concept in concepts if concept.uri is not None
    )

    assert len(raw_keyword.labels) == 1
    assert raw_keyword.labels[0].value == "Test concept"
    assert raw_keyword.id == hal_keyword_concept.id
    assert controlled_concept.id == open_alex_concept.id
    assert any(
        label.value == "Test concept" and label.language == "en"
        for label in controlled_concept.labels
    )
    assert any(
        label.value == "Concept de test" and label.language == "fr"
        for label in controlled_concept.labels
    )
    assert any(
        label.value == "Concepto de test" and label.language == "es"
        for label in controlled_concept.labels
    )
    assert controlled_concept.uri == "http://www.wikidata.org/entity/test_id"
