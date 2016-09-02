import signal
import subprocess

import click
from rq import Worker

import sjs
from sjs.run import initialize_run, end_run, run_started

SUPERVISOR_POLL_FREQUENCY = 60

def disable_signals():
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)

def signal_handler(signal_received, frame):
    disable_signals()
    print("Received signal %s." % signal_received)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def print_status():
    pass

@click.command()
@click.argument('--queue-script', '-q', help='path to executable script that will populate the queue')
@click.option('--skip-pre-checks/--run-pre-checks', default=False)
@click.option('--burst/--stay-alive', '-b/ ', default=True)
@click.option('--auto-requeue-fails', default=False)
@click.option('--resume', '-r', default=False)
def supervisor(queue_script, skip_pre_checks, burst, auto_requeue_fails, resume):
    sjs.load()
    conn = sjs.get_redis_conn()

    if resume:
        if sjs.run_started():
            # we should be ok
            pass
        else:
            print("There is no run to resume. Are you in the right directory?")
            print("Aborting...")
            sys.exit(64)
    else:
        # we are starting a new run
        initialize_run(skip_pre_checks=skip_pre_checks)
        results = subprocess.check_output(queue_script, shell=True, universal_newlines=True)

    run_looks_complete = False
    try:
        while True:
            sleep(SUPERVISOR_POLL_FREQUENCY)

            workers = Worker.all(connection=conn)
            idle_workers = [ w for w in workers if w.state == 'idle' ]
            if len(idle_workers) != len(workers):
                print_status("Workers are still busy.")
                continue

            if len(sjs.get_job_queue()) > 0:
                print_status("Jobs still in queue.")
                continue

            if len(sjs.jobs_failed()) > 0:
                if auto_requeue_fails:
                    print_status("Unresolved jobs in failed queue: requeueing.")
                else:
                    print_status("Unresolved jobs in failed queue.")
                continue

            # if we get here, the job looks like it is done!
            run_looks_complete = True

            # break on --burst,
            # otherwise the --stay-alive flag is enabled and we require a manual SIGINT
            if burst:
                break

    except SystemExit:
        pass

    if run_looks_complete:
        print("Run looks complete, finalizing the run...")
        end_run()
    else:
        print("Run looks incomplete, not finalizing the run. You can restart the supervisor " \
              "script with --resume."
