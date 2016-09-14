from datetime import datetime
import filecmp
import os
import sys

import yaml

import sjs
from sjs.pre_checks import run_pre_queue_checks
from sjs.env_record import save_env_record, read_env_record
from sjs.archive import uncommitted_file_list, create_archive

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

def delete_sjs_running_file():
    os.remove(SJS_RUNNING_FILE)

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

    print("Set up run name and working dir...")
    cwd_dirname = os.path.basename(os.path.normpath(os.getcwd()))
    timestamp = datetime.now().strftime("%Y_%m_%d__%H_%M_%S__%f")
    run_name = "%s_%s" % (cwd_dirname, timestamp)

    working_dir = config['working_dir'] or DEFAULT_WORKING_DIR
    working_dir = os.path.join(working_dir, run_name)
    os.makedirs(working_dir)
    print("Working dir: %s" % working_dir)

    # create sjs running file
    write_sjs_running_file(working_dir)

    print("Saving starting env record")
    env_record_dir = os.path.join(working_dir, 'env_records')
    os.makedirs(env_record_dir)
    save_env_record(os.path.join(env_record_dir, 'env_record_start.yaml'))

    print("Archiving config files")
    file_list = uncommitted_file_list(config['config_dirs'], config['config_ignore'])
    create_archive(file_list, os.path.join(working_dir, 'config.tar.bz'))

    print("Saving run_metadata.yaml file")
    with open(os.path.join(working_dir,'run_metadata.yaml'), 'w') as f:
        f.write(yaml.dump({
            'argv': sys.argv
        }))
    print("=" * 80)
    print("Run is initialized!")
    print("Next steps:")
    print("- queue your jobs to the sub-job server")
    print("- launch workers via your qsub script")

def end_run():
    results = {}
    config = sjs.get_sjs_config()
    working_dir = get_sjs_running_file()
    if not working_dir:
        raise SystemExit("Currently there is no run started (i.e. there is no %s file). " \
            "Are you in the correct directory?" % SJS_RUNNING_FILE)

    print("Saving ending env record and comparing to starting record")
    env_record_dir = os.path.join(working_dir, 'env_records')
    env = save_env_record(os.path.join(env_record_dir, 'env_record_end.yaml'))
    orig_env_record = read_env_record(os.path.join(env_record_dir, 'env_record_start.yaml'))
    results['env_records_match'] = (env == orig_env_record)

    print("Archiving config files and comparing to initial archive")
    config_file_list = uncommitted_file_list(config['config_dirs'], config['config_ignore'])
    config_end_path = os.path.join(working_dir, 'config_end.tar.bz')
    config_start_path = os.path.join(working_dir, 'config.tar.bz')
    create_archive(config_file_list, config_end_path)
    results['configs_match'] = filecmp.cmp(config_start_path, config_end_path, shallow=False)

    print("Outputting results yaml file")
    with open(os.path.join(working_dir, 'results.yaml'), 'w') as f:
        f.write(yaml.dump(results, default_flow_style=False))

    print("Creating final archive including data and put in archive directory.")
    print("This may take awhile...")
    os.makedirs(config['archive_dir'], exist_ok=True)
    archive_path = os.path.join(config['archive_dir'], os.path.basename(working_dir) + '.tar.bz')

    data_dir_list = [ d for d in config['data_dirs'] if os.path.exists(d) ]
    archive_list = [working_dir] + data_dir_list
    create_archive(archive_list, archive_path)
    print("Archive complete and available at: %s" % archive_path)

    delete_sjs_running_file()

    print("FINAL CHECKS:")
    for test, result in results.items():
        if result:
            print("OK: %s" % test)
        else:
            print("FAILURE: %s" % test)
