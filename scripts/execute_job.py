import argparse
import asyncio
import os
import sys

if os.path.basename(os.getcwd()) != "scripts":
    print("Please execute this script from the scripts directory")
    sys.exit(1)
sys.path.append("..")
os.environ["APP_ENV"] = "DEV"

from app.services.jobs.concept_dereferencing_job import (  # pylint: disable=wrong-import-position
    ConceptDereferencingJob,
)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--job_name",
        help="Job name",
        required=True,
        type=str,
    )
    return parser.parse_args()


async def _run_job(job_args):
    job_name = job_args.job_name
    if job_name == "concept_dereferencing":
        print("Running concept_dereferencing job")
        await ConceptDereferencingJob().run()


if __name__ == "__main__":
    args = _parse_args()
    asyncio.run(_run_job(args))
