import click

import sjs
from sjs.run import initialize_run

@click.command()
@click.option('--skip-pre-checks/--run-pre-checks', default=False)
def run_start(skip_pre_checks):
    sjs.load()
    initialize_run(skip_pre_checks=skip_pre_checks)
