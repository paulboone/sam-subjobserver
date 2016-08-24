
import locale
import os
import subprocess
from subprocess import PIPE

from sjs.rq_helper import jobs_failed, jobs_running, jobs_queued

_ENCODING = locale.getpreferredencoding()

def check_repo_is_not_dirty():
    results = subprocess.run(['git','status', '--porcelain'], check=True, stdout=PIPE)
    if results.returncode != 0:
        return "An unhandled error ocurred when attempting to run `git status --porcelain`"
    elif results.stdout:
        message = "These files or directories exist in your deployment that are unaccounted for. " \
                  "They either need to be added to your repo or ignored: \n"
        message += results.stdout.decode(_ENCODING).strip()
        return message

    return None # we're all good here!

def check_repo_is_up_to_date():
    results = subprocess.run(['git','fetch'], check=True, stdout=PIPE)
    if results.returncode != 0:
        return "Can't fetch repo; can't check to see if it is up-to-date."

    results = subprocess.run(['git','status', '-b', '--porcelain'], check=True, stdout=PIPE)
    tracking_line = results.stdout.decode(_ENCODING).strip().split('\n')[0]

    # if the branch is ahead of or behind the tracking branch
    # it will look like '[ahead *]' or '[behind *]' so we just search for the bracket.
    if tracking_line.find('[') >= 0:
        message = "The git repo is either ahead or behind of the github repository. Please either" \
                  " git pull / push or checkout a specific tag / revision.\n"
        message += tracking_line
        return message

    return None # we're all good here!

def check_job_queues_are_empty():
    results = ""

    job_ids = jobs_queued()
    if job_ids:
        results += "Found these queued job_ids: %s" % job_ids

    job_ids = jobs_running()
    if job_ids:
        results += "Found these running job_ids: %s" % job_ids

    job_ids = jobs_failed()
    if job_ids:
        results += "Found these failed job_ids: %s" % job_ids

    return results

def check_log_dir_is_empty():
    results = ""

    log_dir = os.path.join("./","logs")
    logs = os.listdir(log_dir)

    if len(logs) > 0:
        results += "There are %s logs in the log dir; please empty them before continuing." % len(logs)

    return results



PRE_QUEUE_CHECKS=[
    check_repo_is_not_dirty,
    check_repo_is_up_to_date,
    check_job_queues_are_empty,
    check_log_dir_is_empty,
]

PRE_WORKER_CHECKS=[
    check_repo_is_not_dirty,
]

def failure_message(failures):
    messages = [ "\n%s): %s" % (i, msg) for i, msg in enumerate(failures) ]

    message = "***********************************************************\n"
    message += "PRE-CHECK FAILED!\n"
    message += "\n".join(messages) + "\n"

    return message

def run_check_suite(checks, exit_on_fail=False):
    results = [ func() for func in checks ]
    failures = [ fail_message for fail_message in results if fail_message is not None ]
    if failures and exit_on_fail:
        print(failure_message(failures))
        raise SystemExit("PRE-CHECKS FAILED!")

    return (results, failures)

def run_pre_queue_checks(exit_on_fail=True):
    return run_check_suite(PRE_QUEUE_CHECKS, exit_on_fail=exit)

def run_pre_worker_checks(exit_on_fail=True):
    return run_check_suite(PRE_WORKER_CHECKS, exit_on_fail=exit)
