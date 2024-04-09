from fastapi import APIRouter
from loguru import logger
from starlette.background import BackgroundTasks
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.services.jobs.concept_dereferencing_job import ConceptDereferencingJob
from app.config import get_app_settings


router = APIRouter()


@router.post("/concept_dereferencing")
async def post_concept_dereferencing(background_tasks: BackgroundTasks):
    """
    Post a concept dereferencing job
    """
    background_tasks.add_task(ConceptDereferencingJob().run)
    return {"message": "Concept dereferencing job launched"}


# CRON JOBS


@router.on_event("startup")
async def post_concept_dereferencing_cron():
    """
    Post a concept dereferencing job
    """
    conf = _get_job_conf("concept_dereferencing")
    if conf is None:
        return
    if conf["enabled"] is False:
        logger.info("Concept dereferencing job is disabled")
        return
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        ConceptDereferencingJob().run,
        CronTrigger.from_crontab(conf["schedule"]),
    )
    scheduler.start()


def _get_job_conf(job_name: str) -> dict:
    """
    Check if a job is configured in the settings
    """
    settings = get_app_settings().jobs
    for job in settings:
        if job["name"] == job_name:
            return job
    return None
