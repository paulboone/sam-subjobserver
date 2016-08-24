
import re
import subprocess

def archive_file_list(dirs, exclude_patterns):
    uncommitted_files = []
    for d in dirs:
        filelist = subprocess.check_output(['git','ls-files','-o',d], universal_newlines=True)
        uncommitted_files += filelist.strip().split("\n")

    for pattern in exclude_patterns:
        uncommitted_files = [ f for f in uncommitted_files if not re.search(pattern, f) ]

    return uncommitted_files

def create_archive(sources, target):
    subprocess.run(['tar','-czf', target] + sources, check=True)
