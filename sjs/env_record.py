import subprocess

import yaml

def _run_cmd(cmd_list):
    results = subprocess.run(cmd_list, stdout=subprocess.PIPE, check=True, universal_newlines = True,)
    return results.stdout.strip()

def create_env_record():
    env = {}

    env['python_path'] = _run_cmd(['which', 'python'])
    env['python_version'] = _run_cmd(['python', '--version'])

    env['pip_path'] = _run_cmd(['which', 'pip'])
    env['pip_version'] = _run_cmd(['pip', '--version'])
    env['pip_packages'] = _run_cmd(['pip', 'list']).split('\n')

    env['git_describe'] = _run_cmd(['git', 'describe', '--tags'])
    env['git_commit'] = _run_cmd(['git', 'rev-parse', 'HEAD'])

    return env

def save_env_record(path):
    env = create_env_record()
    with open(path, 'w') as f:
        f.write(yaml.dump(env, default_flow_style=False))
    return env

def read_env_record(path):
    with open(path, 'r') as f:
        env = yaml.load(f)
        return env
