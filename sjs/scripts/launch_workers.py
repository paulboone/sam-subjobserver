from datetime import datetime
import os
import signal
import subprocess
import sys

import click

import sjs

def signal_handler(signal_received, frame):
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    print("Received signal %s. Exiting." % signal_received)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

@click.command()
@click.option('--burst/--stay-alive', '-b/ ', default=True)
@click.option('--run-pre-check/--skip-pre-check', default=True)
@click.argument('num_workers', default=1)
def launch_workers(num_workers, burst, run_pre_check):
    os.makedirs("logs", exist_ok=True)

    if run_pre_check:
        print("Running pre-checks...")
        sjs.run_pre_worker_checks(exit_on_fail=True)
        print("OK!")
    else:
        print("Skipping pre-checks!")

    hostname = os.uname()[1]
    timestamp = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")

    print("")
    print("Running on hostname %s" % hostname)
    print("Running at timestamp %s" % timestamp)
    print("Log name template: %s_%s_*.log" % (hostname, timestamp))

    print("")
    rq_args = ""
    if burst:
        print("Running in burst mode. Workers and launch_workers script will exit when there " \
              "is no more work to do")
        rq_args = "-b"
    else:
        print("Workers and launch_workers script will stay alive until killed.")

    print("")
    workers = []
    log_files = []
    cmd = ['rq', 'worker', rq_args, '-c', 'settings.rq_worker_config']
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
