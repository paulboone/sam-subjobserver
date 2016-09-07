import os
import re
import subprocess

def uncommitted_file_list(dirs, exclude_patterns=[]):
    """
    Returns a list of all the files in the passed dirs that are not committed
    to the git repository.
    """
    uncommitted_files = []
    for d in dirs:
        filelist = subprocess.check_output(['git','ls-files','-o',d], universal_newlines=True)
        uncommitted_files += filelist.strip().split("\n")

    for pattern in exclude_patterns:
        uncommitted_files = [ f for f in uncommitted_files if not re.search(pattern, f) ]

    return uncommitted_files

def create_archive(sources, target):
    """
    Creates a bzipped archive at target from a list of sources.

    Sources can be relative or absolute paths. Relative paths are added exactly
    as they are. Any absolute paths are converted to relative paths by first
    changing to the directory containing the directory, and then storing the
    directory in the archive under its basename. So the basename of any
    absolute paths should be unique!
    """
    args = []

    # grab all relative paths first
    args = [ p for p in sources if not os.path.isabs(p) ]

    # create proper argument list for tar that changes directory first using -C
    # before sending the additional source names
    abs_args = [ ('-C', *os.path.split(p)) for p in sources if os.path.isabs(p) ]

    # flatten args for passing to tar
    args += [ a for arg_tuple in abs_args for a in arg_tuple]
    print (" ".join(['tar','-cjf', target] + args))
    subprocess.run(['tar','-cjf', target] + args, check=True)
