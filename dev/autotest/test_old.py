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

def _run(name, args, cwd=None, log_file=None):
    """Run a command, send output to term and to log file."""
    # Header
    msg = "Running: <{}>...".format(name)
    print_h2(msg)
    if log_file: log_file.write(msg)
    # Run
    with subprocess.Popen(
        args, 
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1,
        cwd=cwd, universal_newlines=True,
        ) as p:
        for line in p.stdout: # b'\n'-separated lines FIXME
            sys.stdout.write(line)
            if log_file: log_file.write(line)
    # Close
    returncode = p.returncode
    if returncode < 0:
        msg = "Failed: <{}>, with returncode {}.".format(name, returncode)
        print_fail(msg)
        if log_file: log_file.write(msg)        
    else:
        msg = "Ok: <{}>, with returncode {}.".format(name, returncode)
        print_ok(msg)
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
        bpy.ops.export.fds_case(filepath="/".join((fds_dir,fds_file)))
        # Run FDS on it
        _run(
            name="fds "+fds_file,
            args=['fds',"/".join((fds_dir,fds_file))],
            cwd=fds_dir,
            log_file=None
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
            log_file=None
        )
        args = [
            "diff",
            "/".join((fds_dir,ge1_file)),
            "/".join((ref_fds_dir,ge1_file)),
        ]
        _run(
            name="diff "+ge1_file,
            args=args,
            log_file=None
        )
        msg = "Exporting Blender Scene <{}> to <{}>, done.".format(sc.name,fds_file)
        print_ok(msg)
        if log_file: log_file.write(msg)

def _write_to_file(filepath, text_file):
    """Write text_file to filepath."""
    if text_file is None: text_file = str()
    try:
        with open(filepath, "w") as out_file: out_file.write(text_file)
        return True
    except IOError:
        return False
    
def _run_old(name, args, cwd=None):
    """Run a command and return output string."""
    p = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True, cwd=cwd)
    out, err = p.communicate()
    returncode = p.returncode
    msgs = list()
    msgs.append("Running: <{}>, return code: <{}>".format(name, returncode))
    if err: msgs.extend(("stderr:",err))
    if out: msgs.extend(("stdout:",out))
    msgs.append("8<---")
    return "\n".join(msgs)

def _run_fds(fds_file_path):
    "Run fds on FDS file path. Wait till completion. Check if ok."
    # Init
    fds_file_name = fds_file_path.split("/")[-1]
    fds_file_dir = "/".join(fds_file_path.split("/")[:-1])
    notready_file_path = fds_file_dir + "/" + fds_file_name.split(".")[0] + ".notready"
    # Run
    args = ['fds',fds_file_path]
    cwd = fds_file_dir
    return _run("fds "+fds_file_name,args, cwd)
    # Check existance of .end file
    #if os.path.isfile(notready_file_path): return "FDS calculation <{}>: Error".format(fds_file_name)
    #else: return "FDS calculation <{}>: Ok".format(fds_file_name)

def _run_diff(file_1_path, file_2_path, file_diff_path, excludes=None):
    "Run diff and check if the result is empty."
    # Init
    # Run
    args = ["diff",file_1_path,file_2_path,]
    if excludes:
        for exclude in excludes:
            args.insert(1,"-I")
            args.insert(2,exclude)
    return _run("diff", args)

    # Run
    #p = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    #out, err = p.communicate()
    #rc = p.returncode
    # Check empty diff
    #return "\n".join((" ".join(args),str(rc),err,out))

def test_export_old(blend_file,test_name,test_dir,ref_dir,log_file):
    """Export and check all Scene data-blocks to FDS."""
    
    log = ["Blender file <{}>".format(blend_file),] # FIXME

    # Test full export
    for sc in bpy.data.scenes:
        # Init
        sc_dir        = "/".join((test_dir, sc.bf_head_directory))
        fds_file      = sc.name + ".fds"
        fds_diff_file = fds_file + ".diff"
        ge1_file      = sc.name + ".ge1"
        ge1_diff_file = ge1_file + ".diff"
        # Log
        print_h2("Exporting Blender Scene <{}> to <{}>".format(sc.name,fds_file))
        log.append("Exporting Blender Scene <{}> to <{}>".format(sc.name,fds_file)) # FIXME
        # Clean up sc_dir
        print_h2("Cleaning up Scend dir:",sc.name)
        shutil.rmtree(sc_dir)
        os.mkdir(sc_dir)
        # Export all Scene data-blocks
        print_h2("Exporting:",sc.name)
        bpy.context.screen.scene = sc
        bpy.ops.export.fds_case(filepath=sc_dir+"/"+fds_file)
        # Run FDS on it
        print_h2("Running fds:",fds_file)
        log.append(_run_fds(sc_dir + "/" + fds_file)) # FIXME
        # Run diff on fds and ge1 file
        print_h2("Running diff:",fds_file)
        log.append(_run_diff(sc_dir + fds_file, sc_ref_dir + fds_file, sc_dir + fds_diff_file, excludes=("^! Date:",)))
        log.append(_run_diff(sc_dir + ge1_file, sc_ref_dir + ge1_file, sc_dir + ge1_diff_file))
        # Close
        print("Exporting Blender Scene <{}> to <{}>, done.".format(sc.name,fds_file))
    # Write log
    filepath = "log/{}_{}.log".format(time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime()), test_name)
    _write_to_file(filepath, "\n".join(log))
    print("Testing Blender file <{}>, done.".format(blend_file))

def test_import(blend_file,test_name,test_dir,ref_dir,log_file):
    pass

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
    available_test_types = {"test_export": test_export, "test_import": test_import}
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
