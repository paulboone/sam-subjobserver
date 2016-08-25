import sys

import click

from sjs.env_record import create_env_record

@click.command()
def env_record():
    env = create_env_record()
    sys.stdout.write(yaml.dump(env, default_flow_style=False))
