"""BlenderFDS, io operators"""

import bpy, os.path, sys

from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper, ImportHelper

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

### Import FDS case to new scene

def import_OT_fds_case_menu(self, context):
    """Import an FDS case file into new scene, menu funtion"""
    self.layout.operator("import.fds_case", text="FDS Case (.fds) to new Scene")

class import_OT_fds_case(Operator, ImportHelper):
    """Import an FDS case file into new scene, operator"""
    bl_label = "Import FDS case"
    bl_idname = "import.fds_case"
    bl_description = "Import an FDS case file into a new Blender Scene"
    filename_ext = ".fds"
    filter_glob = bpy.props.StringProperty(default="*.fds", options={'HIDDEN'})

    def execute(self, context):
        return bl_scene_from_fds_case(
            self,
            context,
            **self.as_keywords(ignore=("check_existing", "filter_glob"))
        )

### Import FDS snippet into current scene

class ImportHelperSnippet(ImportHelper):
    """Load an FDS snippet into current scene, operator"""
    bl_label = "Load FDS snippet"
    bl_idname = "import.fds_snippet"
    bl_description = "Load an FDS snippet into current Blender Scene"
    filename_ext = ".fds"
    filter_glob = bpy.props.StringProperty(default="*.fds", options={'HIDDEN'})
    filepath_predefined = sys.path[0] + "/zzz_blenderfds/predefined/"

    def invoke(self, context, event):
        if self.filepath_predefined:
            self.filepath = self.filepath_predefined
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        return bl_scene_from_fds_case(
            self,
            context,
            snippet=True,
            **self.as_keywords(ignore=("check_existing", "filter_glob"))
        )

def import_OT_fds_snippet_menu(self, context):
    """Import an FDS snippet into current scene, menu funtion"""
    self.layout.operator("import.fds_snippet", text="FDS snippet (.fds) to Scene")

class import_OT_fds_snippet(Operator, ImportHelperSnippet):
    bl_idname = "import.fds_snippet"
    filepath_predefined = None

class MATERIAL_OT_bf_load_surf(Operator, ImportHelperSnippet):
    bl_label = "Load predefined SURF"
    bl_idname = "material.bf_load_surf"
    bl_description = "Load a predefined SURF namelist"
    filepath_predefined = sys.path[0] + "/zzz_blenderfds/predefined/SURFs/"    

class SCENE_OT_bf_load_reac(Operator, ImportHelperSnippet):
    bl_label = "Load predefined REAC"
    bl_idname = "scene.bf_load_reac"
    bl_description = "Load a predefined REAC namelist"
    filepath_predefined = sys.path[0] + "/zzz_blenderfds/predefined/REACs/"
    
class SCENE_OT_bf_load_misc(Operator, ImportHelperSnippet):
    bl_label = "Load predefined MISC"
    bl_idname = "scene.bf_load_misc"
    bl_description = "Load a predefined MISC namelist"
    filepath_predefined = sys.path[0] + "/zzz_blenderfds/predefined/MISCs/"

### Import function

def _view3d_view_all(context):
    """View all elements on the 3dview. Override context."""
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = {'area': area, 'region': region, 'edit_object': bpy.context.edit_object}
                    bpy.ops.view3d.view_all(override)

def bl_scene_from_fds_case(operator, context, snippet=False, filepath=""):
    """Import FDS file to a Blender Scene"""

    # Init
    w = context.window_manager.windows[0]
    w.cursor_modal_set("WAIT")
    if snippet:
        # Import into current scene
        sc = context.scene
    else:
        # Create new scene and set as default
        sc = bpy.data.scenes.new("imported_case")
        bpy.context.screen.scene = sc
        sc.set_default_appearance(context)

    # Read file
    DEBUG and print("BFDS: operators_io.bl_scene_from_fds_case: Importing:", filepath)
    try:
        with open(filepath, "r") as infile:
            imported_value = infile.read()
    except EnvironmentError:
        w.cursor_modal_restore()
        operator.report({"ERROR"}, "FDS file not readable, cannot import")
        return {'CANCELLED'}

    # Import to scene
    try: sc.from_fds(context=context, value=imported_value, snippet=snippet)
    except BFException as err:
        w.cursor_modal_restore()
        operator.report({"ERROR"}, str(err))
        return {'CANCELLED'}

    # Adapt 3DView
    _view3d_view_all(context)

    # End
    w.cursor_modal_restore()
    DEBUG and print("BFDS: operators_io.bl_scene_from_fds_case: End.")
    operator.report({"INFO"}, "FDS File imported")
    return {'FINISHED'}

