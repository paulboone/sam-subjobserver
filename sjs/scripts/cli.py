import click
import shutil
import subprocess
import sys

import sjs
from sjs import __version__
from sjs.run import initialize_run, end_run, run_started, delete_sjs_running_file

@click.group(invoke_without_command=True)
@click.option('--version','-v', is_flag=True, default=False)
def cli(version):
    if version:
        print(__version__)

@cli.command(help='Safely kills all the workers for the job_id passed')
@click.argument('qsub_job_id')
def killworkers(qsub_job_id):
    if shutil.which('qsig'):
        subprocess.run(['qsig', '-s', 'SIGINT', qsub_job_id], check=True)
        print("Shutdown signal sent to workers of job_id %s" % qsub_job_id)
    else:
        print("qsig doesn't exist. Do you have the torque module loaded?")


# TODO: Uncomment when launch_workers supports restart.
# @cli.command(help='Restarts all the workers for the job_id passed. ONLY for debugging!')
# @click.argument('qsub_job_id')
# def restartworkers(qsub_job_id):
#     if shutil.which('qsig'):
#         subprocess.run(['qsig', '-s', 'SIGUSR1', qsub_job_id], check=True)
#         print("Restart signal sent to workers of job_id %s" % qsub_job_id)
#     else:
#         print("qsig doesn't exist. Do you have the torque module loaded?")

@cli.command(help='Aborts the current run. WARNING: YOU STILL HAVE TO KILL THE WORKERS MANUALLY OR WITH sjs killworkers')
@click.option('--confirm', '-y', is_flag=True, default=False, help="confirms the abort")
def abort(confirm):
    if not run_started():
        print("No run started here. Are you in the right directory?")
        sys.exit(1)

    if confirm or click.confirm("Are you sure you want to abort the run?"):
        delete_sjs_running_file()
        print("Run aborted!")
    else:
        print("Run NOT aborted!")


@cli.command(help="start a new run.")
@click.option('--skip-pre-checks/--run-pre-checks', default=False)
def start(skip_pre_checks):
    """
    Starts a new run, if one isn't already running.

    Runs all pre-checks, creates any necessary directories, archives the configs, records
    any arguments, and creates an env_record.
    """
    sjs.load()
    initialize_run(skip_pre_checks=skip_pre_checks)

@cli.command(help='finalize a run')
def finalize():
    """
    Finalizes the run, archives the config and all data directories, and outputs status.
    """
    sjs.load()
    end_run()
