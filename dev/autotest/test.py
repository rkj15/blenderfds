#!python3
# test.py <http://blenderfds.org/>.
# Copyright (C) 2016 Emanuele Gissi

import bpy, shutil, os, sys, time
from subprocess import Popen, PIPE

def _write_to_file(filepath, text_file):
    """Write text_file to filepath"""
    if text_file is None: text_file = str()
    try:
        with open(filepath, "w") as out_file: out_file.write(text_file)
        return True
    except IOError:
        return False

def _run(name, args, cwd=None):
    """Run a command and return output string"""
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

def test_export():
    "Export all Scene of opened Blender file to FDS file using the menu Operator, check the results"
    # Init
    filepath_split = bpy.data.filepath.split("/")
    blend_file     = filepath_split[-1]
    test_dir       = "/".join(filepath_split[:-1])
    test_name      = blend_file.split(".")[0]
    ref_dir        = test_dir + "/ref"
    log         = ["Blender file <{}>".format(blend_file),]
    print("Testing Blender file <{}>".format(blend_file))
    # Test full export
    for sc in bpy.data.scenes:
        # Init
        sc_dir        = "/".join((test_dir, sc.bf_head_directory))
        sc_ref_dir    = "/".join((ref_dir,  sc.bf_head_directory))
        fds_file      = sc.name + ".fds"
        fds_diff_file = fds_file + ".diff"
        ge1_file      = sc.name + ".ge1"
        ge1_diff_file = ge1_file + ".diff"
        # Log
        log.append("Exporting Blender Scene <{}> to <{}>".format(sc.name,fds_file))
        print("Exporting Blender Scene <{}> to <{}>".format(sc.name,fds_file))
        # Clean up sc_dir
        print("Cleaning up dir:",sc.name)
        shutil.rmtree(sc_dir)
        os.mkdir(sc_dir)
        # Export all Scene data-blocks
        print("Exporting:",sc.name)
        bpy.context.screen.scene = sc
        bpy.ops.export.fds_case(filepath=sc_dir+"/"+fds_file)
        # Run FDS on it
        print("Running fds:",fds_file)
        log.append(_run_fds(sc_dir + "/" + fds_file)) # FIXME
        # Run diff on fds and ge1 file
        print("Running diff:",fds_file)
        log.append(_run_diff(sc_dir + fds_file, sc_ref_dir + fds_file, sc_dir + fds_diff_file, excludes=("^! Date:",)))
        log.append(_run_diff(sc_dir + ge1_file, sc_ref_dir + ge1_file, sc_dir + ge1_diff_file))
        # Close
        print("Exporting Blender Scene <{}> to <{}>, done.".format(sc.name,fds_file))
    # Write log
    filepath = "log/{}_{}.log".format(time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime()), test_name)
    _write_to_file(filepath, "\n".join(log))
    print("Testing Blender file <{}>, done.".format(blend_file))

def test_import():
    pass

def main():
    import argparse
    # Get arguments
    argv = sys.argv
    if "--" not in argv: argv = []  # as if no args are passed
    else: argv = argv[argv.index("--") + 1:]  # get all args after "--"
    # Manage arguments
    usage_text = (
        "Run blender in background mode with this script:"
        "  blender --background --python " + __file__ + " -- [options]"
    )
    parser = argparse.ArgumentParser(description=usage_text)
    parser.add_argument("--type", dest="test_type", type=str, required=True, help="Test type")
    args = parser.parse_args(argv)
    # Init
    available_test_types = {"test_export": test_export, "test_import": test_import}
    test_type = args.test_type
    # Init
    filepath_split = bpy.data.filepath.split("/")
    blend_file     = filepath_split[-1]
    test_dir       = "/".join(filepath_split[:-1])
    test_name      = blend_file.split(".")[0]
    ref_dir        = test_dir + "/ref"
    errors         = list()    
    # Exec test
    available_test_types[test_type]()
    
if __name__ == "__main__":
    main()
