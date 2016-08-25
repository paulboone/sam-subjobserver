import click

import sjs
from sjs.run import end_run

@click.command()
def run_end():
    sjs.load()
    end_run()
