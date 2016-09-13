import click

import sjs
from sjs import __version__
from sjs.run import initialize_run, end_run

@click.group(invoke_without_command=True)
@click.option('--version','-v', is_flag=True, default=False)
def cli(version):
    if version:
        print(__version__)

@cli.command(help="start a new run.")
@click.option('--skip-pre-checks/--run-pre-checks', default=False)
def start(skip_pre_checks, version):
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
