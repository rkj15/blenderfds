#!/usr/bin/python3
# BlenderFDS automated test <http://blenderfds.org/>.
# Copyright (C) 2016 Emanuele Gissi
# Released under the terms of the GNU GPL version 3 or any later version.

import bpy, shutil, os, time, sys
import subprocess

# from .term_colors import * # FIXME
def print_h1(msg): print("\033[1;34m{}\033[0m".format(msg))
def print_h2(msg): print("\033[1;35m{}\033[0m".format(msg))
def print_ok(msg): print("\033[1;32m{}\033[0m".format(msg))
def print_warn(msg): print("\033[1;33m{}\033[0m".format(msg))
def print_fail(msg): print("\033[1;31m{}\033[0m".format(msg))

def _run(name, args, cwd=None, log_file=None, returncodes={0:(True,"Ok")}):
    """Run a command, send output to term and to log file."""
    # Header
    msg = "Processing <{}>...".format(name)
    print_h2(msg)
    if log_file: print(msg, file=log_file)
    # Run
    with subprocess.Popen(
        args, 
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1,
        cwd=cwd, universal_newlines=True,
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

def test_export(blend_file,test_name,test_dir,ref_dir,log_file=None):
    """Export and check all Scene data-blocks to FDS."""
    # Test full export
    for sc in bpy.data.scenes:
        # Init
        fds_dir       = "/".join((test_dir, sc.bf_head_directory))
        ref_fds_dir   = "/".join((ref_dir, sc.bf_head_directory))
        fds_file      = sc.name + ".fds"
        fds_diff_file = fds_file + ".diff"
        ge1_file      = sc.name + ".ge1"
        ge1_diff_file = ge1_file + ".diff"
        # Log
        print_h2("Exporting Blender Scene <{}> to <{}>".format(sc.name,fds_file))
        # Clean up fds_dir
        print_h2("Cleaning up Scene dir")
        shutil.rmtree(fds_dir)
        os.mkdir(fds_dir)
        # Export all Scene data-blocks
        print_h2("Exporting")
        bpy.context.screen.scene = sc
        bpy.ops.export_scene.fds_case(filepath="/".join((fds_dir,fds_file)))
        # Run FDS on it
        _run(
            name="fds "+fds_file,
            args=['fds',"/".join((fds_dir,fds_file))],
            cwd=fds_dir,
            log_file=None,
            returncodes={0:(True,"Simulation ok"),-11:(False,"Core dump")},
        )
        # Run diff on fds and ge1 file
        args = [
            "diff",
            "-I","^! Date:",
            "/".join((fds_dir,fds_file)),
            "/".join((ref_fds_dir,fds_file)),
        ]
        _run(
            name="diff "+fds_file,
            args=args,
            log_file=None,
            returncodes={0:(True,"No differences"),1:(False,"Differences reported")},
        )
        args = [
            "diff",
            "/".join((fds_dir,ge1_file)),
            "/".join((ref_fds_dir,ge1_file)),
        ]
        _run(
            name="diff "+ge1_file,
            args=args,
            log_file=None,
            returncodes={0:(True,"No differences"),1:(False,"Differences reported")},
        )
        # Log
        msg = "Exporting Blender Scene <{}> to <{}>, done.\n".format(sc.name,fds_file)
        print_h1(msg)
        if log_file: log_file.write(msg)

def test_import(fds_file,test_name,test_dir,ref_dir,log_file=None):
    # Import into new Scene data-blocks
    print_h2("Importing")
    bpy.ops.import_scene.fds_case(filepath="/".join((test_dir,fds_file)))
    bpy.ops.wm.save_mainfile(filepath=test_dir + "/" + sc.name + ".blend")

def main():
    # Output
    filepath_split = bpy.data.filepath.split("/")
    blend_file = filepath_split[-1]
    print_h1("Testing Blender file <{}>".format(blend_file))
    # Get arguments
    import argparse, sys
    argv = sys.argv
    if "--" not in argv: argv = []  # no args are passed
    else: argv = argv[argv.index("--") + 1:]  # get all args after "--"
    # Manage arguments
    usage_text = (
        "Run blender in background mode with this script:"
        "  blender --background --python " + __file__ + " -- [python-options]"
    )
    parser = argparse.ArgumentParser(description=usage_text)
    parser.add_argument("--type", dest="test_type", type=str, required=True, help="Test type")
    args = parser.parse_args(argv)
    # Get test
#    available_test_types = {"test_export": test_export, "test_import": test_import} FIXME
    available_test_types = {"test_export": test_export,}
    test_type = args.test_type
    # Exec test
    available_test_types[test_type](
        blend_file = blend_file,
        test_name  = blend_file.split(".")[0],
        test_dir   = "/".join(filepath_split[:-1]),
        ref_dir    = "ref",
        log_file   = None,
    )
    
if __name__ == "__main__":
    main()
