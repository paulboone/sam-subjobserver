from datetime import datetime
import os
import signal
import subprocess
import sys

import click

import sjs
from sjs.run import get_sjs_running_file, SJS_RUNNING_FILE
from sjs.env_record import save_env_record, read_env_record

def signal_handler(signal_received, frame):
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    print("Received signal %s. Exiting." % signal_received)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

@click.command()
@click.option('--burst/--stay-alive', '-b/ ', default=True)
@click.option('--run-pre-checks/--skip-pre-checks', default=True)
@click.argument('num_workers', default=1)
def launch_workers(num_workers, burst, run_pre_checks):
    os.makedirs("logs", exist_ok=True)

    if run_pre_checks:
        print("Running pre-checks...")
        sjs.run_pre_worker_checks(exit_on_fail=True)
        print("OK!")
    else:
        print("Skipping pre-checks!")

    working_dir = get_sjs_running_file()
    if not working_dir:
        raise SystemExit("Currently there is no run started (i.e. there is no %s file). " \
            "Are you in the correct directory?" % SJS_RUNNING_FILE)

    hostname = os.uname()[1]
    timestamp = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")

    # compare env_record at start of run with this one
    env_record_dir = os.path.join(working_dir, 'env_records')
    env_record_path = os.path.join(env_record_dir, "%s_%s" %(hostname, timestamp))
    env = save_env_record(env_record_path)
    orig_env_record = read_env_record(os.path.join(env_record_dir, 'env_record_start.yaml'))
    if env != orig_env_record:
        print("env_record of this machine does not match env record of original machine! " \
            "Aborting launch workers! Please see %s to compare manually" % (env_record_path))
        raise SystemExit("Env records do not match, aborting launch workers!")



    print("")
    print("Running on hostname %s" % hostname)
    print("Running at timestamp %s" % timestamp)
    print("Log name template: %s_%s_*.log" % (hostname, timestamp))
    print("Env record path: %s" % env_record_path)

    print("")
    rq_args = []
    if burst:
        print("Running in burst mode. Workers and launch_workers script will exit when there " \
              "is no more work to do")
        rq_args += ["-b"]
    else:
        print("Workers and launch_workers script will stay alive until killed.")

    print("")
    workers = []
    log_files = []

    sjs.load()
    sjs_config = sjs.get_sjs_config()
    redis_cfg = sjs_config['redis']
    redis_url = "redis://%s:%s/%s" % (redis_cfg['host'], redis_cfg['port'], redis_cfg['db'])
    rq_args += ["-u", redis_url]
    rq_args += [sjs_config['queue']]
    cmd = ['rq', 'worker', *rq_args]

    for i in range(num_workers):
        logname = 'logs/%s_%s_%s.log' % (hostname, timestamp, i)
        print("Launching worker #%s with log file %s" % (i, logname))

        log = open(logname,'w')
        proc = subprocess.Popen(cmd, stdout=log, stderr=log)

        workers.append(proc)
        log_files.append(log)

    print("")
    print("Waiting for workers to exit...")
    try:
        for w in workers:
            w.wait()
    except SystemExit:
        # if this process is forced to exit, we kill the workers, and wait for them to
        # exit, before finally closing the log files.
        print("... killing any workers")
        os.killpg(os.getpid(), signal.SIGTERM)
        for w in workers:
            w.wait()
    finally:
        for f in log_files:
            f.close()

    print("")
    print("All done!")
