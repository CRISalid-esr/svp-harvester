Job: Concept Dereferencing
===========================

Purpose
----------

This background job is responsible for dereferencing concepts in the database, if they failed to be dereferenced during the harvesting process.
It will update the concepts in the database with the information from the external source.

Run the job
-----------

It can be run with three different processes:

- Using a script that runs the job once. This script is located at `scripts/concept_dereferencing.py`. To run it, execute the following command:

..  code-block:: bash

    python3 execute_job.py --job_name concept_dereferencing 

- Using a POST request to the API endpoint `/api/v1/jobs/concept_dereferencing`
- Setting up a cron job to run the script periodically. It can be configured in the file `jobs.yml`.