import yaml
import os.path

from redis import Redis
from rq import Queue

DEFAULT_CONFIG_LOCATION=os.path.join('./', 'settings', 'sjs.yaml')
DEFAULT_TIMEOUT = 8640000 # 100 days

job_queue = None
redis_conn = None
sjs_config = None

def load(filepath=DEFAULT_CONFIG_LOCATION):
    global sjs_config, redis_conn, job_queue

    if not os.path.exists(filepath):
        print("Cannot find the configuration yaml file at %s!" % filepath)
        print("Try running this command from your project directory.")
        # do not throw an error here because this is likely just the user running
        # the system locally.
        return False

    with open(filepath, 'r') as yaml_file:
        sjs_config = yaml.load(yaml_file)
        sjs_config['archive_dir'] = os.path.expanduser(sjs_config['archive_dir'])
        sjs_config['working_dir'] = os.path.expanduser(sjs_config['working_dir'])
        sjs_config['data_dirs'] = [ os.path.expanduser(os.path.normpath(d))
                                    for d in sjs_config['data_dirs'] ]
        sjs_config['config_dirs'] = [ os.path.expanduser(os.path.normpath(d))
                                      for d in sjs_config['config_dirs'] ]

        if 'max_seconds_per_job' not in sjs_config:
            sjs_config['max_seconds_per_job'] = DEFAULT_TIMEOUT

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

def get_sjs_config():
    return sjs_config
