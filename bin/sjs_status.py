#!/usr/bin/env python3
import sys

import yaml
from redis import Redis
from rq import Worker, Queue

import sjs

filepath = sjs.DEFAULT_CONFIG_LOCATION
if len(sys.argv) > 1:
    filepath = sys.argv[1]

if not sjs.load(filepath):
    raise SystemExit()

redis_conn = sjs.get_redis_conn()

def job_string(j):
    if j is None:
        return "-"
    return "  %s (%s): %s" % (j.get_id(), j.get_status(), j.get_call_string())


print("## WORKERS ##")
ws = Worker.all(connection=redis_conn)

for w in sorted(ws, key=lambda x: x.name):
    print("worker %s: %s" % (w.name, job_string(w.get_current_job())))

print("")
print("## QUEUES ##")
qs = Queue.all(connection=redis_conn)
for q in sorted(qs, key=lambda x: x.name):
    print("queue %s:" % q.name)
    for j in q.get_jobs():
        print(job_string(j))
