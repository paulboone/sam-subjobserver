
import locale
import os
import subprocess
from subprocess import PIPE

import sjs
from sjs.rq_helper import jobs_failed, jobs_running, jobs_queued

_ENCODING = locale.getpreferredencoding()

def check_git_describe_has_tags():
    results = subprocess.run(['git','describe', '--tags'], stdout=PIPE, stderr=PIPE, universal_newlines=True)
    if results.returncode != 0:
        return ['`git describe --tags` failed presumably because there are no tags. Error message: \n' +
                 results.stderr.strip()]
    return []

def check_repo_is_not_dirty():
    results = subprocess.run(['git','status', '--porcelain'], check=True, stdout=PIPE)
    if results.returncode != 0:
        return "An unhandled error ocurred when attempting to run `git status --porcelain`"
    elif results.stdout:
        message = "These files or directories exist in your deployment that are unaccounted for. " \
                  "They either need to be added to your repo or ignored: \n"
        message += results.stdout.decode(_ENCODING).strip()
        return [message]

    return [] # we're all good here!

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
        return [message]

    return [] # we're all good here!]

def check_job_queues_are_empty():
    results = []

    job_ids = jobs_queued()
    if job_ids:
        results += ["Found these queued job_ids: %s" % job_ids]

    job_ids = jobs_running()
    if job_ids:
        results += ["Found these running job_ids: %s" % job_ids]

    job_ids = jobs_failed()
    if job_ids:
        results += ["Found these failed job_ids: %s" % job_ids]

    return results

def check_data_dirs_are_empty():
    config = sjs.get_sjs_config()
    data_dirs = config['data_dirs']
    messages = []
    for d in data_dirs:
        files = os.listdir(d)

        if len(files) > 0:
            message = "There are %s log(s) in the '%s' dir; please remove before continuing." \
                        % (len(files), d)
            messages += [message]

    return messages

PRE_QUEUE_CHECKS=[
    check_git_describe_has_tags,
    check_repo_is_not_dirty,
    check_repo_is_up_to_date,
    check_job_queues_are_empty,
    check_data_dirs_are_empty,
]

PRE_WORKER_CHECKS=[
    check_repo_is_not_dirty,
]

def failure_message(failures):
    message = "***********************************************************\n"
    message += "PRE-CHECK FAILED!"

    for i, message_tuple in enumerate(failures):
        name, message_list = message_tuple

        message += "\n\n%s) %s:\n" % (i, name)
        message += "\n".join(message_list)

    message += "\n"
    return message

def run_check_suite(checks, exit_on_fail=False):
    results = [ (func.__name__,func()) for func in checks ]
    failures = [ tup for tup in results if tup[1] ]
    if failures:
        print(failure_message(failures))
        if exit_on_fail:
            raise SystemExit("PRE-CHECKS FAILED!")

    return (results, failures)

def run_pre_queue_checks(exit_on_fail=True):
    return run_check_suite(PRE_QUEUE_CHECKS, exit_on_fail=exit)

def run_pre_worker_checks(exit_on_fail=True):
    return run_check_suite(PRE_WORKER_CHECKS, exit_on_fail=exit)
