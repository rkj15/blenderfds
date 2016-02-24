"""BlenderFDS, test utilities"""

import subprocess, shutil, os, sys
from .term_colors import *

def run(name, args, cwd=None, log_file=None, returncodes={0:(True,"Ok")}, shell=False):
    """Run a command, send output to term and to log file."""
    # Header
    msg = "Processing <{}>...".format(name)
    print_h2(msg)
    if log_file: print(msg, file=log_file)
    # Run
    with subprocess.Popen(
        args, 
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1,
        cwd=cwd, universal_newlines=True, shell=shell,
        ) as p:
        for line in p.stdout:
            sys.stdout.write(line) # print() adds unwanted \n
            if log_file: log_file.write(line)
    # Close
    returncode = p.returncode
    ok, msg = returncodes.get(returncode, (False,"Unknown"))
    msg = "Process <{}> exited, returncode {}: {}".format(name, returncode, msg)
    if ok: print_ok(msg)
    else: print_fail(msg)
    if log_file: log_file.write(msg)

def clean_dir(directory):
    """Delete and recreate directory"""
    print("Cleaning up directory: "+ directory)
    shutil.rmtree(directory)
    os.mkdir(directory)
