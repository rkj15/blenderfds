"""BlenderFDS, panels"""

from bpy.types import Panel

from ..fds.lang import SN_HEAD, SN_TIME, SN_DUMP, SN_MISC, SN_REAC, OP_SURF_ID

### Scene panels

class SCENE_PT_BF():
    bl_label = "BlenderFDS Case"
    bl_idname = "SCENE_PT_BF"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    
    bf_namelist = None

    def draw_header(self, context):
        layout = self.layout
        element = context.scene
        self.bl_label = self.bf_namelist(element).draw_header(context, layout)
        
    def draw(self, context):
        layout = self.layout
        element = context.scene
        # Panel
        self.bf_namelist(element).draw(context, layout)
        
class SCENE_PT_BF_HEAD(SCENE_PT_BF, Panel):
    bl_idname = "SCENE_PT_BF_HEAD"
    bf_namelist = SN_HEAD

    def draw(self, context):
        layout = self.layout
        element = context.scene
        # Restore cursor in case of unhandled Exception
        w = context.window_manager.windows[0]
        w.cursor_modal_restore()
        # Panel
        self.bf_namelist(element).draw(context, layout)
        # Other operators
        row = layout.row()
        row.operator("scene.bf_show_fds_code", text="Show FDS Code")
        row.operator("scene.bf_props_to_scene", text="Copy To")

class SCENE_PT_BF_TIME(SCENE_PT_BF, Panel):
    bl_idname = "SCENE_PT_BF_TIME"
    bf_namelist = SN_TIME

class SCENE_PT_BF_MISC(SCENE_PT_BF, Panel):
    bl_idname = "SCENE_PT_BF_MISC"
    bf_namelist = SN_MISC

class SCENE_PT_BF_REAC(SCENE_PT_BF, Panel):
    bl_idname = "SCENE_PT_BF_REAC"
    bf_namelist = SN_REAC

class SCENE_PT_BF_DUMP(SCENE_PT_BF, Panel):
    bl_idname = "SCENE_PT_BF_DUMP"
    bf_namelist = SN_DUMP


### Object panel

class OBJECT_PT_BF_MESH(Panel):
    bl_label = "BlenderFDS Geometric Entity"
    bl_idname = "OBJECT_PT_BF_MESH"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    
    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return ob and ob.type == "MESH" and not ob.bf_is_tmp

    def draw_header(self, context):
        layout = self.layout
        element = context.active_object
        self.bl_label = element.bf_namelist.draw_header(context, layout)

    def draw(self, context):
        layout = self.layout
        element = context.active_object
        # Restore cursor in case of unhandled Exception
        w = context.window_manager.windows[0]
        w.cursor_modal_restore()
        # Panel
        split = layout.split(.6)  # namelist
        split.prop(element, "bf_namelist_cls", text="")
        row = split.row(align=True)  # aspect
        row.prop(element, "show_transparent", icon="GHOST", text="")
        row.prop(element, "draw_type", text="")
        row.prop(element, "hide", text="")
        row.prop(element, "hide_select", text="")
        row.prop(element, "hide_render", text="")
        element.bf_namelist.draw(context, layout)
        row = layout.row()
        if element.bf_has_tmp: row.operator("scene.bf_del_all_tmp_objects", text="Hide FDS Geometry")
        else: row.operator("object.bf_show_fds_geometries", text="Show FDS Geometry")
        row.operator("object.bf_show_fds_code", text="Show FDS Code")
        row.operator("object.bf_props_to_sel_obs", text="Copy To")

class OBJECT_PT_BF_EMPTY(Panel):
    bl_label = "BlenderFDS Empty (Section of namelists)"
    bl_idname = "OBJECT_PT_BF_EMPTY"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    
    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return ob and ob.type == "EMPTY" and not ob.bf_is_tmp

    def draw(self, context):
        layout = self.layout
        element = context.active_object
        # Restore cursor in case of unhandled Exception
        w = context.window_manager.windows[0]
        w.cursor_modal_restore()
        # Panel
        layout.template_ID(context.scene.objects, "active") # ID
        layout.prop(element, "bf_fyi", text="", icon="INFO") # FYI
        row = layout.row()
        if element.bf_has_tmp: row.operator("scene.bf_del_all_tmp_objects", text="Hide FDS Geometry")
        else: row.label(text="")
        row.operator("object.bf_show_fds_code", text="Show FDS Code")
        row.operator("object.bf_props_to_sel_obs", text="Copy To")

class OBJECT_PT_BF_TMP(Panel):
    bl_label = "BlenderFDS Temporary Object"
    bl_idname = "OBJECT_PT_BF_TMP"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    
    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return ob and ob.bf_is_tmp

    def draw(self, context):
        layout = self.layout
        element = context.active_object
        # Restore cursor in case of unhandled Exception
        w = context.window_manager.windows[0]
        w.cursor_modal_restore()
        # Panel
        layout.operator("scene.bf_del_all_tmp_objects")

### Material panel

class MATERIAL_PT_BF(Panel):
    bl_label = "BlenderFDS Boundary Condition"
    bl_idname = "MATERIAL_PT_BF"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    @classmethod
    def poll(cls,context):
        ma = context.material
        ob = context.active_object
        return ma and ob and ob.type == "MESH" and not ob.bf_is_tmp \
            and OP_SURF_ID in ob.bf_namelist.all_bf_props
            # show the panel only when relevant

    def draw_header(self, context):
        layout = self.layout
        element = context.material
        self.bl_label = element.bf_namelist.draw_header(context, layout)

    def draw(self, context):
        layout = self.layout
        element = context.material
        # Restore cursor in case of unhandled Exception
        w = context.window_manager.windows[0]
        w.cursor_modal_restore()
        # Panel
        split = layout.split(.7) # namelist
        split.prop(element, "bf_namelist_cls", text="")
        row = split.row(align=True) # aspect
        row.prop(element, "diffuse_color", text="")
        row.prop(element, "alpha", text="")
        element.bf_namelist.draw(context, layout)
        # Other operators
        row = layout.row()
        row.operator("material.bf_show_fds_code", text="Show FDS Code")
        row.operator("material.bf_surf_to_sel_obs", text="Assign To")

