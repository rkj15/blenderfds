"""BlenderFDS, menus and other ui mods"""

import bpy
from bpy.types import Panel, Header, Menu

from . import operators_io

DEBUG = False

### Register/Unregister

def register():
    """Register menus and other ui mods"""
    # io menus
    bpy.types.INFO_MT_file_export.prepend(operators_io.export_OT_fds_case_menu)
    bpy.types.INFO_MT_file_import.prepend(operators_io.import_OT_fds_snippet_menu)
    bpy.types.INFO_MT_file_import.prepend(operators_io.import_OT_fds_case_menu)
    # Load blenderfds settings menu
    bpy.types.INFO_MT_file.draw = _INFO_MT_file_draw
    # Additional mods (user's preference)
    if bpy.context.user_preferences.addons["zzz_blenderfds"].preferences.bf_pref_simplify_ui:
        # Simplify info editor menu
        bpy.types.INFO_MT_editor_menus.draw_menus = _INFO_MT_editor_menus_draw_menus
        bpy.types.INFO_MT_help.draw = _INFO_MT_help_draw
        bpy.types.INFO_MT_add.draw = _INFO_MT_add_draw
        # Simplify view3d tools
        bpy.types.VIEW3D_PT_tools_add_object.draw = _VIEW3D_PT_tools_add_object_draw
        # Simplify space properties header
        _rewire_space_properties_header()
        # Treat (rewire or unregister) unused Blender bpy.types
        _treat_unused_bl_classes()

def unregister():
    """Unregister menus and other ui mods"""
    # info menu
    bpy.types.INFO_MT_editor_menus.draw_menus = _INFO_MT_editor_menus_draw_menus_tmp

### Rewire draw functions

def _INFO_MT_editor_menus_draw_menus(layout, context): # beware: here is "layout, context"!
    layout.menu("INFO_MT_file")
    layout.menu("INFO_MT_window")
    layout.menu("INFO_MT_help")

def _INFO_MT_editor_menus_draw_menus_tmp(layout, context): # beware: here is "layout, context"!
    row = layout.row()
    row.alert = True
    row.operator("wm.quit_blender", text="Restart neeeded", icon='QUIT')

def _INFO_MT_file_draw(self, context):
    layout = self.layout

    layout.operator_context = 'INVOKE_AREA'
    layout.operator("wm.read_homefile", text="New", icon='NEW')
    layout.operator("wm.open_mainfile", text="Open...", icon='FILE_FOLDER')
    layout.menu("INFO_MT_file_open_recent", icon='OPEN_RECENT')
    layout.operator("wm.revert_mainfile", icon='FILE_REFRESH')
    layout.operator("wm.recover_last_session", icon='RECOVER_LAST')
    layout.operator("wm.recover_auto_save", text="Recover Auto Save...", icon='RECOVER_AUTO')

    layout.separator()

    layout.operator_context = 'EXEC_AREA' if context.blend_data.is_saved else 'INVOKE_AREA'
    layout.operator("wm.save_mainfile", text="Save", icon='FILE_TICK')

    layout.operator_context = 'INVOKE_AREA'
    layout.operator("wm.save_as_mainfile", text="Save As...", icon='SAVE_AS')
    layout.operator_context = 'INVOKE_AREA'
    layout.operator("wm.save_as_mainfile", text="Save Copy...", icon='SAVE_COPY').copy = True

    layout.separator()

    layout.operator("screen.userpref_show", text="User Preferences...", icon='PREFERENCES')

    layout.operator_context = 'INVOKE_AREA'
    layout.operator("wm.save_homefile", icon='SAVE_PREFS')
    layout.operator("wm.bf_load_blenderfds_settings", icon='LOAD_FACTORY')
    layout.operator("wm.read_factory_settings", icon='LOAD_FACTORY')

    layout.separator()

    layout.operator_context = 'INVOKE_AREA'
    layout.operator("wm.link", text="Link", icon='LINK_BLEND')
    layout.operator("wm.append", text="Append", icon='APPEND_BLEND')

    layout.separator()

    layout.menu("INFO_MT_file_import", icon='IMPORT')
    layout.menu("INFO_MT_file_export", icon='EXPORT')

    layout.separator()

    layout.menu("INFO_MT_file_external_data", icon='EXTERNAL_DATA')

    layout.separator()

    layout.operator_context = 'EXEC_AREA'
    if bpy.data.is_dirty and context.user_preferences.view.use_quit_dialog:
        layout.operator_context = 'INVOKE_SCREEN'  # quit dialog
    layout.operator("wm.quit_blender", text="Quit", icon='QUIT')

def _INFO_MT_help_draw(self, context):
    layout = self.layout
    layout.operator("wm.url_open", text="BlenderFDS Manual", icon='HELP').url = "https://code.google.com/p/blenderfds/wiki/Wiki_Home"
    layout.operator("wm.url_open", text="BlenderFDS Website", icon='URL').url = "http://www.blenderfds.org"
    layout.separator()
    layout.operator("wm.url_open", text="Blender Manual", icon='HELP').url = "http://www.blender.org/manual"
    layout.operator("wm.url_open", text="Blender Website", icon='URL').url = "http://www.blender.org"

def _INFO_MT_add_draw(self, context):
    layout = self.layout
    layout.operator_context = 'EXEC_REGION_WIN'
    layout.menu("INFO_MT_mesh_add", icon='OUTLINER_OB_MESH')
    layout.operator("object.empty_add", text="Empty", icon='OUTLINER_OB_EMPTY')

def _VIEW3D_PT_tools_add_object_draw(self, context):
    layout = self.layout
    col = layout.column(align=True)
    self.draw_add_mesh(col, label=True)

def _unused_header_draw(self, context):
    """Generic unused header draw function"""
    layout = self.layout
    row = layout.row(align=True)
    row.template_header()

### Rewire space properties

# Rewire space properties header

_sp_items = (
    ('SCENE','Scene','Scene','SCENE_DATA',1),
    ('OBJECT','Object','Object','OBJECT_DATA',3),
    ('MATERIAL','Material','Material','MATERIAL',5),
    ('MODIFIER','Modifiers','Object modifiers','MODIFIER',10),
)

def _sp_items_update(self, context):
    if self.bf_sp_context == context.space_data.context: return # no update needed, also for second update
    for trial in (self.bf_sp_context,'OBJECT','MATERIAL','SCENE'):  # try several ordered choices
        try: context.space_data.context = trial
        except TypeError: continue # not available for current entity
        else:
            self.bf_sp_context = trial
            break

def _PROPERTIES_HT_header_draw(self, context):
    layout = self.layout
    row = layout.row()
    row.template_header()
    row.prop(context.window_manager, "bf_sp_context", expand=True, icon_only=True)

def _rewire_space_properties_header():
    """Rewire SpaceProperties header, less contexts shown"""
    bpy.types.WindowManager.bf_sp_context = bpy.props.EnumProperty(items=_sp_items, update=_sp_items_update, default="OBJECT")
    bpy.types.PROPERTIES_HT_header.draw = _PROPERTIES_HT_header_draw

### Treat (rewire or unregister) unused Blender bpy.types

# Configuration

_used_bl_space_type = (
    "TEXTEDITOR", "TEXT_EDITOR", "USER_PREFERENCES", "CONSOLE",
    "FILE_BROWSER", "INFO", "OUTLINER",
)

_used_headers = (
    'Header', 'PROPERTIES_HT_header', 'VIEW3D_HT_header',
)

_used_panels = (
    'Panel',
    'SCENE_PT_BF_HEAD', 'SCENE_PT_BF_TIME', 'SCENE_PT_BF_DUMP', 'SCENE_PT_BF_MISC', 'SCENE_PT_BF_REAC',
    'OBJECT_PT_BF_MESH', 'OBJECT_PT_BF_EMPTY', 'OBJECT_PT_BF_TMP',
    'MATERIAL_PT_BF',
    'DATA_PT_modifiers', 'RENDER_PT_render',
)

_unused_panels = (
        "VIEW3D_PT_view3d_shading", "VIEW3D_PT_view3d_motion_tracking",
        "VIEW3D_PT_transform_orientations", "VIEW3D_PT_view3d_name",
        "VIEW3D_PT_context_properties",
    )

_used_panel_by_bl_space_type = "PROPERTIES", "VIEW_3D"
_used_panel_by_bl_category = "Tools", "Create", "Relations", "Options", "Grease Pencil"
_used_panel_by_bl_region_type = "UI"

# Treat unused classes

def _treat_unused_bl_classes():
    """Treat (rewire or unregister) unused Blender bpy.types"""
    for bt_name in dir(bpy.types):
        # if DEBUG: print("BFDS: Treated Class:", bt_name)
        # Init
        bt_cls = getattr(bpy.types, bt_name, None)
        bt_bl_space_type = getattr(bt_cls, "bl_space_type", None)
        # Surely used bts
        if bt_bl_space_type in _used_bl_space_type: continue
        # Other Headers and Panels
        # Panels
        if issubclass(bt_cls, Panel):
            if bt_name in _used_panels: continue
            if bt_name not in _unused_panels and bt_bl_space_type in _used_panel_by_bl_space_type:
                bt_bl_category = getattr(bt_cls, "bl_category", None)
                if bt_bl_category and bt_bl_category in _used_panel_by_bl_category: continue
                bt_bl_region_type = getattr(bt_cls, "bl_region_type", None)
                if bt_bl_region_type and bt_bl_region_type in _used_panel_by_bl_region_type: continue
            # If nothing else applies, unregister the Panel
            if DEBUG: print("BFDS: Unregister Panel:", bt_name)
            bpy.utils.unregister_class(bt_cls)
            continue
        # Headers
        if issubclass(bt_cls, Header):
            if bt_name in _used_headers: continue
            if DEBUG: print("BFDS: Rewire Header:", bt_name)
            bt_cls.draw = _unused_header_draw # Unused header, rewire its draw function
            continue
