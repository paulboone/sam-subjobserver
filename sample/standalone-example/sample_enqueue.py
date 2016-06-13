#
# prior to running this, you must:
#
# module load python/anaconda3-2.3.0-rhel

from rq import Queue
from redis import Redis

from time import sleep

from sample_job import job_that_takes_a_long_time


# use local redis (for testing and development)
redis_conn = Redis()

# uncomment to use SAM job server redis (for production work on SAM)
# redis_conn = Redis(host='app1.sam.pitt.edu', port=6379, db=0)

# replace 'sample_queue' with your queue name
# if you do this, make sure you run your worker on that queue, e.g. `rq worker {your_queue_name}`
q = Queue('sample_queue', connection=redis_conn)

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