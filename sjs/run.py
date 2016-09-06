from datetime import datetime
import filecmp
import os
import sys

import yaml

import sjs
from sjs.pre_checks import run_pre_queue_checks
from sjs.env_record import save_env_record, read_env_record
from sjs.archive import archive_file_list, create_archive

DEFAULT_WORKING_DIR = os.path.expanduser("~/.sjs")
DEFAULT_ARCHIVE_DIR = os.path.expanduser("~/sjs_archive")

SJS_RUNNING_FILE = '.sjs_running'

def run_started():
    if get_sjs_running_file():
        return True
    return False

def get_sjs_running_file():
    if os.path.exists(SJS_RUNNING_FILE):
        with open(SJS_RUNNING_FILE, 'r') as f:
            working_dir = f.read().strip()
            return working_dir

    return None

def write_sjs_running_file(working_dir):
    with open(SJS_RUNNING_FILE, 'w') as f:
        f.write(working_dir)

def initialize_run(skip_pre_checks=False):

    # setup .sjs_running_file
    if get_sjs_running_file():
        print("%s file already exists. Are you in the middle of a run / did the last run fail " \
            "without finishing successfully? If you are certain there is nothing else that is " \
            "running, delete the file and try again." % SJS_RUNNING_FILE)
        raise SystemExit("Aborting due to pre-existing %s file." % SJS_RUNNING_FILE)

    if not skip_pre_checks:
        run_pre_queue_checks(exit_on_fail=True)

    config = sjs.get_sjs_config()

    # set up run name and working dir
    cwd_dirname = os.path.basename(os.path.normpath(os.getcwd()))
    timestamp = datetime.now().strftime("%Y_%m_%d__%H_%M_%S__%f")
    run_name = "%s_%s" % (cwd_dirname, timestamp)

    working_dir = config['working_dir'] or DEFAULT_WORKING_DIR
    working_dir = os.path.join(working_dir, run_name)
    os.makedirs(working_dir)

    # create sjs running file
    write_sjs_running_file(working_dir)

    # save starting env record
    env_record_dir = os.path.join(working_dir, 'env_records')
    os.makedirs(env_record_dir)
    save_env_record(os.path.join(env_record_dir, 'env_record_start.yaml'))

    # archive config files
    file_list = archive_file_list(config['config_dirs'], config['config_ignore'])
    create_archive(file_list, os.path.join(working_dir, 'config.tar.gz'))

    # save run_metadata.yaml file
    with open(os.path.join(working_dir,'run_metadata.yaml'), 'w') as f:
        f.write(yaml.dump({
            'argv': sys.argv
        }))

def end_run():
    results = {}
    config = sjs.get_sjs_config()
    working_dir = get_sjs_running_file()
    if not working_dir:
        raise SystemExit("Currently there is no run started (i.e. there is no %s file). " \
            "Are you in the correct directory?" % SJS_RUNNING_FILE)

    # save ending env record and compare to starting record
    env_record_dir = os.path.join(working_dir, 'env_records')
    env = save_env_record(os.path.join(env_record_dir, 'env_record_end.yaml'))
    orig_env_record = read_env_record(os.path.join(env_record_dir, 'env_record_start.yaml'))
    results['env_records_match'] = (env == orig_env_record)

    # archive config files and compare to initial archive
    config_file_list = archive_file_list(config['config_dirs'], config['config_ignore'])
    config_end_path = os.path.join(working_dir, 'config_end.tar.gz')
    config_start_path = os.path.join(working_dir, 'config.tar.gz')
    create_archive(config_file_list, config_end_path)
    results['configs_match'] = filecmp.cmp(config_start_path, config_end_path, shallow=False)

    # archive data directories
    data_file_list = [ d for d in config['data_dirs'] if os.path.exists(d) ]
    create_archive(data_file_list, os.path.join(working_dir, 'data.tar.gz'))

    # output results yaml file
    with open(os.path.join(working_dir, 'results.yaml'), 'w') as f:
        f.write(yaml.dump(results, default_flow_style=False))

    # archive working dir and put in archive directory
    os.makedirs(config['archive_dir'], exist_ok=True)
    archive_path = os.path.join(config['archive_dir'], os.path.basename(working_dir) + '.tar.gz')
    create_archive([working_dir], archive_path)

    # delete sjs running file
    os.remove(SJS_RUNNING_FILE)
