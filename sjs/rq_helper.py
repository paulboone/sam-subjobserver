#!/usr/bin/env python3
"""

"""

from time import sleep
import os
import sys
from datetime import datetime

import sjs
from rq.queue import get_failed_queue
from rq.job import Job
from rq.registry import StartedJobRegistry
import yaml

def jobs_failed():
    failed_queue = get_failed_queue(connection=sjs.get_redis_conn())
    return failed_queue.get_job_ids()

def requeue_failed_jobs():
    failed_queue = get_failed_queue(connection=sjs.get_redis_conn())

    jobs_to_requeue = failed_queue.get_job_ids()
    for job_id in jobs_to_requeue:
        failed_queue.requeue(job_id)

    return jobs_to_requeue

def jobs_running():
    registry = StartedJobRegistry(name=sjs.get_sjs_config()['queue'], connection=sjs.get_redis_conn())
    return registry.get_job_ids()

def jobs_queued():
    jobs_queue = sjs.get_job_queue()
    return jobs_queue.get_job_ids()

def timestamp():
    return datetime.now().strftime("%Y_%m_%d__%H_%M_%S")

# def last_generation():
#     return session.query(func.max(Material.generation)).filter(Material.run_id == run_id).one()[0]

def manage_run_results(job_id):
    return Job.fetch(job_id, connection=sjs.get_redis_conn()).result
