import click

import sjs
from sjs.run import initialize_run, end_run

@click.group()
def cli():
    "sub job server"
    pass

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
