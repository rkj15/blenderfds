"""BlenderFDS, export operators"""

import bpy, os.path

from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper

from ..exceptions import BFException
from ..utils import is_writable, write_to_file


DEBUG = True

### Export scene to FDS

def export_OT_fds_case_menu(self, context):
    """Export current scene to FDS case, menu function"""
    # Prepare default filepath
    filepath = "{0}.fds".format(os.path.splitext(bpy.data.filepath)[0])
    directory = os.path.dirname(filepath)
    basename = os.path.basename(filepath)
    # If the context scene contains path and basename, use them
    sc = context.scene
    if sc.bf_head_directory: directory = sc.bf_head_directory
    if sc.name: basename = "{0}.fds".format(bpy.path.clean_name(sc.name))
    # Call the exporter operator
    filepath = "{0}/{1}".format(directory, basename)
    self.layout.operator("export.fds_case", text="Scene to FDS Case (.fds)").filepath = filepath

class export_OT_fds_case(Operator, ExportHelper):
    """Export current Blender Scene to an FDS case file, operator"""
    bl_label = "Export FDS"
    bl_idname = "export.fds_case"
    bl_description = "Export current Blender Scene as an FDS case file"
    filename_ext = ".fds"
    filter_glob = bpy.props.StringProperty(default="*.fds", options={'HIDDEN'})

    def execute(self, context):
        # Init
        w = context.window_manager.windows[0]
        w.cursor_modal_set("WAIT")
        sc = context.scene
        # Prepare FDS filepath
        DEBUG and print("BFDS: export_OT_fds_case: Exporting current Blender Scene '{}' to FDS case file".format(sc.name))
        filepath = self.filepath
        if not filepath.lower().endswith('.fds'): filepath += '.fds'
        filepath = bpy.path.abspath(filepath)
        # Check FDS filepath writable
        if not is_writable(filepath):
            w.cursor_modal_restore()
            self.report({"ERROR"}, "FDS file not writable, cannot export")
            return {'CANCELLED'}
        # Prepare FDS file
        try: fds_file = sc.to_fds_case(context=context)
        except BFException as err:
            w.cursor_modal_restore()
            self.report({"ERROR"}, str(err))
            return{'CANCELLED'}
        # Write FDS file
        if not write_to_file(filepath, fds_file):
            w.cursor_modal_restore()
            self.report({"ERROR"}, "FDS file not writable, cannot export")
            return {'CANCELLED'}
        # GE1 description file requested?
        if sc.bf_dump_render_file:
            # Prepare GE1 filepath
            DEBUG and print("BFDS: export_OT_fds_case: Exporting current Blender Scene '{}' to .ge1 render file".format(sc.name))
            filepath = filepath[:-4] + '.ge1'
            if not is_writable(filepath):
                w.cursor_modal_restore()
                self.report({"ERROR"}, "GE1 file not writable, cannot export")
                return {'CANCELLED'}              
            # Prepare GE1 file
            try: ge1_file = sc.to_ge1(context=context)
            except BFException as err:
                w.cursor_modal_restore()
                self.report({"ERROR"}, str(err))
                return{'CANCELLED'}
            # Write GE1 file
            if not write_to_file(filepath, ge1_file):
                w.cursor_modal_restore()
                self.report({"ERROR"}, "GE1 file not writable, cannot export")
                return {'CANCELLED'}      
        # End
        w.cursor_modal_restore()
        DEBUG and print("BFDS: export_OT_fds_case: End.")
        self.report({"INFO"}, "FDS case exported")
        return {'FINISHED'}

