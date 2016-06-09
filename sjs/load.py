import yaml
import os.path

from redis import Redis
from rq import Queue

DEFAULT_CONFIG_LOCATION='hpc.yaml'

job_queue = None
redis_conn = None
sjs_config = None

def load(filepath=DEFAULT_CONFIG_LOCATION):
    global sjs_config, redis_conn, job_queue

    if not os.path.exists(filepath):
        print("file does not exist?")
        # do not throw an error here because this is likely just the user running
        # the sfystem locally.
        return False

    with open(filepath, 'r') as yaml_file:
        sjs_config = yaml.load(yaml_file)

    redis_conn = Redis(**sjs_config['redis'])
    if 'queue' in sjs_config:
        job_queue = Queue(sjs_config['queue'],
            connection=redis_conn,
            default_timeout=sjs_config['max_seconds_per_job']
        )
        return True

    return False

def get_job_queue():
    return job_queue

def get_redis_conn():
    return redis_conn
