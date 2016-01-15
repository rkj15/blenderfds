"""BlenderFDS, preferences panel"""

from bpy.types import AddonPreferences
from bpy.props import BoolProperty

# Get preference value like this:
# bpy.context.user_preferences.addons["zzz_blenderfds"].preferences.bf_pref_simplify_ui

class BFPreferences(AddonPreferences):
    bl_idname = "zzz_blenderfds"

    bf_pref_simplify_ui = BoolProperty(
            name="Simplify Blender User Interface (Blender restart needed)",
            description="Simplify Blender User Interface (Blender restart needed)",
            default=True,
            )

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "bf_pref_simplify_ui")
