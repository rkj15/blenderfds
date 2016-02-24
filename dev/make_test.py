#!/usr/bin/python3
# Run BlenderFDS automated tests <http://blenderfds.org/>.
# Copyright (C) 2016 Emanuele Gissi
# Released under the terms of the GNU GPL version 3 or any later version.

# Test
# - export all example cases
# - import some fds files and export, then compare with ref

import subprocess

blender = "/home/egissi/Documenti/Argomenti/BlenderFDS/blender"
examples_dir = "/home/egissi/Documenti/Argomenti/BlenderFDS/git/blenderfds/examples"
test_names = "round-room","plume","uni-build" # list of test names

def _run_test(test_dir, test_name):
    args = (
            blender,
            test_dir + "/" + test_name + ".blend",
            "--background",
            "--python",
            test_dir + "/test/run.py"
    )
    subprocess.call(args)    

def main():
    for test_name in test_names:
        print("\nTest name:", test_name)
        test_dir = examples_dir + "/" + test_name
        _run_test(test_dir, test_name)
        
    #test_name = "couch" FIXME
               
    print("\nmake_test.py: Done.")
    
if __name__ == "__main__":
    main()
