#
# prior to running this, you must:
#
# module load python/anaconda3-2.3.0-rhel

import sys
from time import sleep

import sjs

from sample_job import job_that_takes_a_long_time

filepath = sjs.DEFAULT_CONFIG_LOCATION
if len(sys.argv) > 1:
    filepath = sys.argv[1]

if not sjs.load(filepath):
    raise SystemExit()

sjs.run_pre_queue_checks(exit_on_fail=True)

redis_conn = sjs.get_redis_conn()
q = sjs.get_job_queue()

# enqueue sample jobs
jobs = []
jobs.append(q.enqueue(job_that_takes_a_long_time, 10))
jobs.append(q.enqueue(job_that_takes_a_long_time, 60))

# NOTE:
# Just because a job is queued, doesn't mean there are any workers to run it. If you are testing,
# you should go ahead and and start a worker with `rq worker`.

# WARNING: you would normally be done here!
# But for this test code, we're going to wait around, get the output and print.
# NOT AT ALL RECOMMENDED FOR PRODUCTION CODE

sleep(200)

for j in jobs:
    print(j.result)
