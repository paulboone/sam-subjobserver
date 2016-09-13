import curses
from datetime import datetime
import signal
import subprocess
import sys
from time import sleep

import click
from rq import Worker, Queue

import sjs
from sjs.run import initialize_run, end_run, run_started
from sjs.curses_fullscreen import curses_fullscreen

sjs.load()
conn = sjs.get_redis_conn()
stdscr = None
maxyx = None
def disable_signals():
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)

def signal_handler(signal_received, frame):
    disable_signals()
    raise SystemExit("Received signal %s." % signal_received)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def job_string(j):
    if j is None:
        return "-"
    func_name = j.func_name
    args = j.get_call_string()[len(func_name) + 1:-1]
    return "%s() | STATUS %s | QUEUED_AT %s | ID %s | ARGS %s" % (
           func_name, j.get_status(), j.enqueued_at, j.get_id(), args)

def print_autoy(message, yadd=0, xadd=0):
    global ypos
    ypos += yadd
    if ypos < maxyx[0]:
        stdscr.addstr(ypos, xadd, message[0:maxyx[1]-xadd])
        ypos += 1

def print_status(status_message=""):
    global ypos
    global maxyx

    ypos = 0
    stdscr.clear()
    if curses.is_term_resized(*maxyx):
        maxyx = stdscr.getmaxyx()
        curses.resizeterm(*maxyx)

    print_autoy(datetime.now().strftime("%c"))

    if status_message:
        print_autoy(status_message, yadd=1)


    ws = Worker.all(connection=conn)
    print_autoy("WORKERS (%s): " % len(ws), yadd=1)
    if ws:
        for w in sorted(ws, key=lambda x: x.name):
            print_autoy("worker %s: %s" % (w.name, job_string(w.get_current_job())), xadd=2)
    else:
        print_autoy("no workers", xadd=2)

    qs = Queue.all(connection=conn)
    print_autoy("QUEUES: ", yadd=1)
    for q in sorted(qs, key=lambda x: x.name):
        print_autoy("%s (%s):" % (q.name, len(q)), xadd=2)

        for j in sorted(q.get_jobs(), key=lambda x: x.enqueued_at):
            print_autoy(job_string(j), xadd=4)

    stdscr.refresh()

@click.command()
@click.option('--auto-finalize', '-af', is_flag=True, default=False)
@click.option('--auto-requeue-fails', '-ar', is_flag=True, default=False)
@click.option('--interval', '-n', default=60, help='update interval in seconds')
@click.option('--skip-run-check', is_flag=True, default=False)
def monitor(auto_finalize, auto_requeue_fails, interval, skip_run_check):
    global stdscr
    global maxyx

    if not skip_run_check and not run_started():
        print("There is no run to resume. Are you in the right directory?")
        print("Aborting.")
        sys.exit(64)

    first_time_through = True
    run_looks_complete = False
    run_finalized = False
    try:
        with curses_fullscreen() as stdscr:
            maxyx = stdscr.getmaxyx()
            while True:
                if first_time_through:
                    first_time_through = False
                else:
                    sleep(interval)

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
                        sjs.requeue_failed_jobs()
                    else:
                        print_status("Unresolved jobs in failed queue.")
                    continue

                run_looks_complete = True
                if auto_finalize:
                    break
                else:
                    print_status("Run looks complete but --auto-finalize is off. Waiting for user to cntl-c.")



    except SystemExit as e:
        print(e.code)

    if run_looks_complete:
        if auto_finalize:
            print("Run looks complete.")
            print("Finalizing the run...")
            end_run()
            print("Finished!")
        else:
            print("The run looks complete but was not auto-finalized.")
            print("You should verify the run is complete, then run 'sjs finalize'")
