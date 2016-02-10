#!python3
# Make BlenderFDS test <http://blenderfds.org/>.
# Copyright (C) 2016 Emanuele Gissi

# Test
# - export all example cases
# - import some fds files and export, then compare with ref

import subprocess

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Setup

blender = "/home/egissi/Documenti/Argomenti/BlenderFDS/blender"
examples_dir = "/home/egissi/Documenti/Argomenti/BlenderFDS/git/blenderfds/examples"
test_names = "round-room","plume","uni-build" # list of test names

# Main

def main():
    print(bcolors.HEADER + "\nmake_test.py: BlenderFDS automated testing suite" + bcolors.ENDC)
    for test_name in test_names:
        print(bcolors.OKBLUE + "\nTest name:", test_name + bcolors.ENDC)
        test_dir = examples_dir + "/" + test_name
        args = (
                blender,
                test_dir + "/" + test_name + ".blend",
                "--background",
                "--python",
                "./test.py",
                "--", # end blender arguments
                "--type", "export-test"
        )
        subprocess.call(args)
        
    #test_name = "couch" FIXME
               
    print(bcolors.OKGREEN + "\nmake_test.py: Done." + bcolors.ENDC)
    
if __name__ == "__main__":
    main()
