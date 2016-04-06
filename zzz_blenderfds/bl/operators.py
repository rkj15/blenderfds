"""BlenderFDS, operators"""

import bpy, os, sys
from bpy.types import Operator
from bpy.props import *

from ..types import BFProp
from ..exceptions import BFException
from .. import fds
from .. import geometry

# TODO search operators fro MATL_ID, PROP_ID...

### Dialog box operator

class WM_OT_bf_dialog(Operator):
    bl_label = "BlenderFDS"
    bl_idname = "wm.bf_dialog"
    bl_description = "BlenderFDS Dialog"

    type = EnumProperty(
        name = "Type",
        items = (("INFO", "Information", "Information",), ("ERROR", "Error", "Error")),
        description = "Dialog type",
        default="INFO",
    )

    msg = StringProperty(
        name="Message",
        description="Dialog message",
        default="No message",
    )

    description = StringProperty(
        name="Description",
        description="Dialog description",
    )

    def execute(self, context):
        return {'FINISHED'}
 
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text=self.msg, icon=self.type)
        if self.description:
            col.separator()
            descriptions = self.description.splitlines()
            for description in descriptions:
                row = col.row()
                row.label(description)

### Load BlenderFDS Settings

class WM_OT_bf_load_blenderfds_settings(Operator):
    """Load BlenderFDS Settings"""
    bl_label = "Load BlenderFDS settings"
    bl_idname = "wm.bf_load_blenderfds_settings"
    bl_description = "Load default BlenderFDS settings, deleting current data!"

    def invoke(self, context, event): # Ask for confirmation
        wm = context.window_manager
        return wm.invoke_confirm(self, event)

    def execute(self, context):
        # Set default startup.blend
        filepath = os.path.dirname(sys.modules['zzz_blenderfds'].__file__) \
            + "/predefined/bf_startup.blend"
        bpy.ops.wm.open_mainfile(filepath=filepath, load_ui=True, use_scripts=True)
        bpy.ops.wm.save_homefile()
        # Save user preferences
        bpy.ops.wm.save_userpref()
        # Report
        self.report({"INFO"}, "Default BlenderFDS settings loaded")
        return {'FINISHED'}

### DEVC QUANTITY

class OBJECT_OT_bf_set_devc_quantity(Operator):
    bl_label = "Set QUANTITY for DEVC"
    bl_idname = "object.bf_set_devc_quantity"
    bl_description = "Set QUANTITY parameter for DEVC namelist"

    bf_quantity = EnumProperty(
        name="QUANTITY", description="Set QUANTITY parameter for DEVC namelist",
        items=fds.tables.get_quantity_items("D"),
    )
          
    def execute(self, context):
        ob = context.active_object
        ob.bf_quantity = self.bf_quantity
        self.report({"INFO"}, "QUANTITY parameter set")
        return {'FINISHED'}

    def invoke(self, context, event):
        ob = context.active_object
        try: self.bf_quantity = ob.bf_quantity
        except TypeError: ob.bf_quantity = ""
        # Call dialog
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        self.layout.prop(self,"bf_quantity",text="")

### MESH and IJK

class OBJECT_OT_bf_set_cell_size(Operator):
    bl_label = "Set Cell Sizes"
    bl_idname = "object.bf_set_cell_sizes"
    bl_description = "Set MESH cell sizes"

    bf_cell_sizes = FloatVectorProperty(
        name="Desired Cell Sizes [m]", description="Desired MESH cell sizes",
        default=(.2, .2, .2), min=.001, step=1000, precision=3, size=3
    )
    bf_snap_to_origin = BoolProperty(
        name="Snap To Global Origin",
        description="Snap this MESH to global origin while setting desired cell sizes (Object may be scaled and moved)",
        default=False,
    )
    bf_poisson_restriction = BoolProperty(
        name="Poisson Restriction",
        description="Respect FDS Poisson solver restriction on IJK values while setting desired cell sizes (Object may be scaled and moved)",
        default=False,
    )
    
    def draw(self, context):
        layout = self.layout
        ob = context.active_object
        row = layout.row()
        row.prop(self, "bf_cell_sizes")
        row = layout.row()
        row.prop(self, "bf_snap_to_origin")
        row = layout.row()
        row.prop(self, "bf_poisson_restriction")
        
    def execute(self, context):
        ob = context.active_object
        ob_moved = fds.mesh.set_cell_sizes(context, ob, self.bf_cell_sizes, self.bf_snap_to_origin, self.bf_poisson_restriction)
        ob.bf_mesh_ijk_export = True # Set export IJK
        if ob_moved: self.report({"WARNING"}, "MESH cell size set, Object moved and scaled")
        else: self.report({"INFO"}, "MESH cell size set")
        return {'FINISHED'}

    def invoke(self, context, event):
        ob = context.active_object
        # Set default
        self.bf_cell_sizes = fds.mesh.get_cell_sizes(context, ob)
        # Call dialog
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OBJECT_OT_bf_correct_ijk(Operator):
    bl_label = "Correct IJK"
    bl_idname = "object.bf_correct_ijk"
    bl_description = "Correct IJK for FDS Poisson solver"

    def execute(self, context):
        ob = context.active_object
        ob.bf_mesh_ijk = fds.mesh.get_good_ijk(ob.bf_mesh_ijk)
        self.report({"INFO"}, "IJK corrected")
        return {'FINISHED'}

### Create related SURF

class OBJECT_OT_bf_new_related_surf(Operator):
    bl_label = "New Related SURF"
    bl_idname = "object.bf_new_related_surf"
    bl_description = "Create new related SURF"

    def execute(self, context):
        # Create Material and link it to the Object
        ma = bpy.data.materials.new("New SURF")
        ob = context.active_object
        ob.active_material = ma
        ma.bf_export = True
        # Change context (modified panel)
        context.window_manager.bf_sp_context = 'MATERIAL' # Works even with regular UI
        # Return
        self.report({"INFO"}, "New related SURF created")
        return {'FINISHED'}

### Show FDS export string

class _COMMON_bf_show_fds_code():

    def draw(self, context):
        layout = self.layout
        for line in self.bf_fds_code.split("\n"):
            row = layout.row()
            row.label(text=line)
        
    def execute(self, context):
        self.report({"INFO"}, "FDS Code Shown")
        return {'FINISHED'}

    def _get_fds_code(self, context):
        ob = context.active_object
        self.bf_fds_code = ob.to_fds(context)

    def invoke(self, context, event):
        # Init
        w = context.window_manager.windows[0]
        w.cursor_modal_set("WAIT")
        # Get the FDS code
        try: self._get_fds_code(context)
        except BFException as err:
            w.cursor_modal_restore()
            self.report({"ERROR"}, str(err))
            return{'CANCELLED'}
        # Call dialog
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=600)

class OBJECT_OT_bf_show_fds_code(_COMMON_bf_show_fds_code, Operator):
    bl_label = "Show FDS Code From Blender Object"
    bl_idname = "object.bf_show_fds_code"
    bl_description = "Show FDS code exported from Blender Object"

    def _get_fds_code(self, context):
        ob = context.active_object
        self.bf_fds_code = ob.to_fds(context)

class MATERIAL_OT_bf_show_fds_code(_COMMON_bf_show_fds_code, Operator):
    bl_label = "Show FDS Code From Blender Material"
    bl_idname = "material.bf_show_fds_code"
    bl_description = "Show FDS code exported from Blender Material"

    def _get_fds_code(self, context):
        ma = context.active_object.active_material
        self.bf_fds_code = ma.to_fds(context)

class SCENE_OT_bf_show_fds_code(_COMMON_bf_show_fds_code, Operator):
    bl_label = "Show FDS Code From Blender Scene"
    bl_idname = "scene.bf_show_fds_code"
    bl_description = "Show FDS code exported from Blender SCene"

    def _get_fds_code(self, context):
        scene = context.scene
        self.bf_fds_code = scene.to_fds(context)

### Copy properties between elements

def _bf_props_copy(context, source_element, destination_elements):
    """Copy all BFProp from source_element to destination_elements"""
    for bf_prop in BFProp.all:
        try: bpy_value = getattr(source_element, bf_prop.bpy_idname)
        except: continue
        if bf_prop.bf_other.get("copy_protect"): continue # Do not copy protected BFProp
        for destination_element in destination_elements:
            setattr(destination_element, bf_prop.bpy_idname, bpy_value)
            print("BFDS: Copy: {} -> {}: {}='{}'".format(source_element.name, destination_element.name, bf_prop.bpy_idname, bpy_value)) 

class SCENE_OT_bf_copy_props_to_scene(Operator):
    bl_label = "Copy Properties To Scene"
    bl_idname = "scene.bf_props_to_scene"
    bl_description = "Copy these properties to another scene"

    bf_destination_element = StringProperty(name="To scene")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop_search(self, "bf_destination_element", bpy.data, "scenes")        

    def execute(self, context):
        # Get source and destination scenes
        source_element = context.scene
        destination_elements = (bpy.data.scenes.get(self.bf_destination_element, None),) # a tuple!
        if not destination_elements[0]:
            self.report({"WARNING"}, "No destination scene")
            return{'CANCELLED'}
        if not source_element:
            self.report({"WARNING"}, "No source scene")
            return{'CANCELLED'}
        # Copy
        _bf_props_copy(context, source_element, destination_elements)
        self.report({"INFO"}, "Copied to destination scene")
        return {'FINISHED'}

    def invoke(self, context, event):
        # Call dialog
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OBJECT_OT_bf_copy_FDS_properties_to_sel_obs(Operator):
    bl_label = "Copy these properties to other selected objects"
    bl_idname = "object.bf_props_to_sel_obs"
    bl_description = "Copy these properties to other selected objects"

    def invoke(self, context, event): # Ask for confirmation
        wm = context.window_manager
        return wm.invoke_confirm(self, event)

    def execute(self,context):
        if context.mode != 'OBJECT': bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        # Get source and destination objects
        source_element = context.active_object
        destination_elements = set(ob for ob in context.selected_objects if ob.type == "MESH" and ob != source_element)
        if not destination_elements:
            self.report({"WARNING"}, "No destination objects")
            return{'CANCELLED'}
        if not source_element:
            self.report({"WARNING"}, "No source object")
            return{'CANCELLED'}
        # Copy
        _bf_props_copy(context, source_element, destination_elements)
        self.report({"INFO"}, "Copied to selected objects")
        return {'FINISHED'}
        
class MATERIAL_OT_bf_assign_BC_to_sel_obs(Operator):
    bl_label = "Assign this boundary condition to selected objects"
    bl_idname = "material.bf_surf_to_sel_obs"
    bl_description = "Assign this boundary condition to selected objects"

    def invoke(self, context, event): # Ask for confirmation
        wm = context.window_manager
        return wm.invoke_confirm(self, event)

    def execute(self,context):
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        # Get source and destination materials
        source_element = context.active_object
        active_material = source_element.active_material
        destination_elements = set(ob for ob in context.selected_objects if ob.type == "MESH" and ob != source_element)
        if not destination_elements:
            self.report({"WARNING"}, "No destination objects")
            return{'CANCELLED'}
        if not source_element:
            self.report({"WARNING"}, "No source object")
            return{'CANCELLED'}
        if not active_material:
            self.report({"WARNING"}, "No boundary condition to assign")
            return{'CANCELLED'}
        # Loop on objects
        for ob in destination_elements:
            ob.active_material = active_material
            print("BlenderFDS: Assign material '{}' -> {}".format(active_material.name, ob.name))
        # Set myself as exported
        active_material.bf_export = True
        # Return
        self.report({"INFO"}, "Assigned to selected objects")
        return {'FINISHED'}

### Predefined materials

class MATERIAL_OT_bf_set_predefined(Operator): # TODO this operator is not used, no more checks in the UI
    bl_label = "Set Predefined"
    bl_idname = "material.bf_set_predefined"
    bl_description = "Set predefined SURFs: INERT, OPEN, MIRROR..."

    def execute(self, context):
        fds.surf.set_predefined(context)
        self.report({"INFO"}, "Predefined SURFs ok")
        return {'FINISHED'}

### Show exported geometry

class OBJECT_OT_bf_show_fds_geometries(Operator):
    bl_label = "Show FDS Geometries"
    bl_idname = "object.bf_show_fds_geometries"
    bl_description = "Show geometries as exported to FDS"

    def execute(self, context):
        # Init
        w = context.window_manager.windows[0]
        w.cursor_modal_set("WAIT")
        if context.mode != 'OBJECT': bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        ob = context.object
        msgs = list()
        err_msgs = list()
        # Manage XB: get coordinates, show them in a tmp object, prepare msg
        xbs = None
        msg = None
        try:  xbs, msg  = geometry.to_fds.ob_to_xbs(context, ob)
        except BFException as err:
            w.cursor_modal_restore()
            self.report({"ERROR"}, str(err))
            return{'CANCELLED'}
        if msg: msgs.append(msg)
        if xbs:
            ob_tmp = geometry.from_fds.xbs_to_ob(xbs, context, bf_xb=ob.bf_xb, name="Shown {} XBs".format(ob.name))
            geometry.tmp_objects.set(context, ob, ob_tmp)
        # Manage XYZ: get coordinates, show them in a tmp object, prepare msg
        xyzs = None
        msg = None
        try: xyzs, msg = geometry.to_fds.ob_to_xyzs(context, ob)
        except BFException as err:
            w.cursor_modal_restore()
            self.report({"ERROR"}, str(err))
            return{'CANCELLED'}
        if msg: msgs.append(msg)
        if xyzs:
            ob_tmp = geometry.from_fds.xyzs_to_ob(xyzs, context, bf_xyz=ob.bf_xyz, name="Shown {} XYZs".format(ob.name))
            geometry.tmp_objects.set(context, ob, ob_tmp)
        # Manage PB*: get coordinates, show them in a tmp object, prepare msg
        pbs  = None
        msg = None        
        try: pbs, msg  = geometry.to_fds.ob_to_pbs(context, ob)
        except BFException as err:
            w.cursor_modal_restore()
            self.report({"ERROR"}, str(err))
            return{'CANCELLED'}
        if msg: msgs.append(msg)
        if pbs:
            ob_tmp = geometry.from_fds.pbs_to_ob(pbs, context, bf_pb=ob.bf_pb, name="Shown {} PBs".format(ob.name))
            geometry.tmp_objects.set(context, ob, ob_tmp)
        # Set report
        if msgs: report = {"INFO"}, "; ".join(msgs)
        elif xbs or xyzs or pbs: report = {"INFO"}, "FDS geometries shown"
        else: report = {"WARNING"}, "No geometry to show"
        # Return
        w.cursor_modal_restore()
        self.report(*report)
        return{'FINISHED'}

class SCENE_OT_bf_del_all_tmp_objects(Operator):
    bl_label = "Hide Temporary Objects"
    bl_idname = "scene.bf_del_all_tmp_objects"
    bl_description = "Delete all temporary objects"

    def execute(self, context):
        geometry.tmp_objects.del_all(context)
        self.report({"INFO"}, "All temporary objects deleted")
        return {'FINISHED'}

### Open text editor with right text displayed
    
class SCENE_OT_bf_edit_head_free_text(Operator):
    bl_label = "Edit"
    bl_idname = "scene.bf_edit_head_free_text"
    bl_description = "Edit free text file in separate editor"

    def execute(self, context):
        bf_head_free_text = fds.head.set_free_text_file(context, context.scene)
        self.report({"INFO"}, "See '{}' in the text editor".format(bf_head_free_text))
        return {'FINISHED'}

### Set TAU_Q ramp according to norms

class MATERIAL_OT_bf_set_tau_q(Operator):
    bl_label = "Set t² Ramp"
    bl_idname = "material.set_tau_q"
    bl_description = "Set t² ramp and HRRPUA"

    bf_burner_area = FloatProperty(
        name="Est.d Burner Area [m²]",
        description="Estimated burner area used for HRRPUA. Correct it for eventual hidden burner surfaces.",
        min=0., precision=2, step=100
    ) # unit="AREA" this would need correction
    bf_hrr_max = FloatProperty(
        name="HRR Max [kW]",
        description="Maximum HRR achieved at the end of the αt² ramp.",
        min=0., precision = 1, step=1000
    )
    bf_growth_rate = EnumProperty(
        name = "Growth Rate",
        description="Standardized growth rate for the HRR αt² ramp.",
        items = (
            ("SLOW", "Slow (600 s)", "Slow growth rate (600 s)"),
            ("MEDIUM", "Medium (300 s)", "Medium growth rate (300 s)"),
            ("FAST", "Fast (150 s)", "Fast growth rate (150 s)"),
            ("ULTRA-FAST", "Ultra fast (75 s)", "Ultra fast growth rate (75 s)"),
        ),
        default = "FAST",
    )
    bf_reference_hrr = EnumProperty(
        name = "Reference HRR",
        description="Reference HRR αt² ramp standard.",
        items = (
            ("US", "US, 1000 BTU/s (1055 kW)", "US, 1000 BTU/s (1055 kw)"),
            ("EN", "Eurocode, 1000 kW", "Eurocode, 1000 kW"),
        ),
        default = "EN",
    )
    bf_set_fyi = BoolProperty(name="Set FYI",default=False) # The user shall choose and understand implications

    def execute(self, context):
        ma = context.object.active_material
        reference_hrr = {"US":1055., "EN":1000.}[self.bf_reference_hrr]
        time = {"SLOW":600., "MEDIUM":300., "FAST":150., "ULTRA-FAST":75.}[self.bf_growth_rate]
        ma.bf_tau_q = -time * (self.bf_hrr_max / reference_hrr) ** .5
        ma.bf_hrrpua = self.bf_hrr_max / self.bf_burner_area
        if self.bf_set_fyi:
            ma.bf_fyi = "Est.d area {:.2f} m², HRR max {:.0f} kW, {} t² ramp ({})".format(
                self.bf_burner_area,
                self.bf_hrr_max,
                self.bf_growth_rate.lower(),
                self.bf_reference_hrr
            )
        self.report({'INFO'}, "TAU_Q and HRRPUA set")
        return {'FINISHED'}

    def invoke(self, context, event):
        ma = context.object.active_material
        # Calc burner area
        burner_area = 0.
        obs = (ob for ob in context.scene.objects \
            if ob.type == "MESH" and ob.bf_export \
            and ob.active_material == ma \
            and ob.bf_namelist.all_bf_props.get("OP_SURF_ID"))
        for ob in obs: burner_area += geometry.geom_utils.get_global_area(context, ob)
        # Set defaults to estimated values
        self.bf_burner_area = burner_area
        self.bf_hrr_max = ma.bf_hrrpua * burner_area
        # Call dialog
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

