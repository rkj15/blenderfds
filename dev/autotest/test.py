#!python3
# test.py <http://blenderfds.org/>.
# Copyright (C) 2016 Emanuele Gissi

import bpy, subprocess, shutil, os, sys

def _run_fds(fds_file_path):
    "Run fds on FDS file path. Wait till completion. Check if ok."
    fds_file_name = fds_file_path.split("/")[-1]
    fds_file_dir = "/".join(fds_file_path.split("/")[:-1])
    notready_file_path = fds_file_dir + "/" + fds_file_name.split(".")[0] + ".notready"
    subprocess.call(['fds',fds_file_path], cwd=fds_file_dir)
    # Check existance of .end file
    if os.path.isfile(notready_file_path): raise Exception("Error in FDS calculation:", fds_file_name)

def _run_diff(file_1_path, file_2_path, file_diff_path, excludes=None):
    "Run diff and check if the result is empty."
    with open(file_diff_path, 'wb', 0) as file:
        args = ["diff",file_1_path,file_2_path,]
        if excludes:
            for exclude in excludes:
                args.insert(1,"-I")
                args.insert(2,exclude)
        subprocess.call(args,stdout=file)
    # CHeck empty diff
    if os.stat(file_diff_path).st_size != 0: raise Exception("Error in diff:", file_diff_path)
    os.remove(file_diff_path)

def _export_scene(sc):
    "Export Scene to FDS file, using the menu Operator."
    # Init
    filepath_split = bpy.data.filepath.split("/")
    test_dir = "/".join(filepath_split[:-1])
    ref_dir = test_dir + "/ref"
    sc_dir = "/".join((test_dir, sc.bf_head_directory))
    sc_ref_dir = "/".join((ref_dir, sc.bf_head_directory))
    fds_file = sc.name + ".fds"
    print("Blender Scene <{}> to <{}>".format(sc.name,fds_file))
    # Clean up sc_dir
    shutil.rmtree(sc_dir)
    os.mkdir(sc_dir)
    # Set current Scene and export all Scene data-blocks
    bpy.context.screen.scene = sc
    bpy.ops.export.fds_case(filepath=sc_dir+"/"+fds_file)

def test_export():
    "Export all Scene of opened Blender file to FDS file using the menu Operator, check the results"
    # Init
    filepath_split = bpy.data.filepath.split("/")
    blend_file     = filepath_split[-1]
    test_dir       = "/".join(filepath_split[:-1])
    test_name      = blend_file.split(".")[0]
    ref_dir        = test_dir + "/ref"
    # Test full export
    for sc in bpy.data.scenes:
        # Init
        sc_dir        = "/".join((test_dir, sc.bf_head_directory))
        sc_ref_dir    = "/".join((ref_dir,  sc.bf_head_directory))
        fds_file      = sc.name + ".fds"
        fds_diff_file = fds_file + ".diff"
        ge1_file      = sc.name + ".ge1"
        ge1_diff_file = ge1_file + ".diff"
        print("Blender Scene <{}> to <{}>".format(sc.name,fds_file))
        # Clean up sc_dir
        shutil.rmtree(sc_dir)
        os.mkdir(sc_dir)
        # Export all Scene data-blocks
        bpy.context.screen.scene = sc
        bpy.ops.export.fds_case(filepath=sc_dir+"/"+fds_file)
        # Run FDS on it
        _run_fds(sc_dir + "/" + fds_file)
        # Run diff on fds and ge1 file
#        _run_diff(sc_dir + fds_file, sc_ref_dir + fds_file, sc_dir + fds_diff_file, excludes=("^! Date:", "^! * voxels,","^! Generated"))
# FIXME time can be slightly different!
        _run_diff(sc_dir + fds_file, sc_ref_dir + fds_file, sc_dir + fds_diff_file, excludes=("^!",))
        _run_diff(sc_dir + ge1_file, sc_ref_dir + ge1_file, sc_dir + ge1_diff_file)

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
    test_type = args.test_type
    #
    if test_type == "export-test": test_export() # FIXME align nomenclature
    elif test_type == "import-test": test_import() # FIXME align nomenclature
    
if __name__ == "__main__":
    main()
