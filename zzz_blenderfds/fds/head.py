"""BlenderFDS, FDS HEAD routines"""

import bpy

def set_free_text_file(context, scene):
    """Set free text file name, then try to open it in shown Blender Text Editor area."""
    # Check name existence
    if not scene.bf_head_free_text:
        # Empty field
        scene.bf_head_free_text = "HEAD free text ({})".format(scene.name)
    # Check text existence
    if scene.bf_head_free_text not in bpy.data.texts:
        # No linked file, create
        bpy.data.texts.new(scene.bf_head_free_text)
    # Search for the Text Editor
    area_te = None
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if 'TEXT_EDITOR' == area.type:
                area_te = area
                break
    # If Text Editor is displayed, show requested text
    if area_te:
        area_te.spaces[0].text = bpy.data.texts[scene.bf_head_free_text]
    # Return free text file name
    return scene.bf_head_free_text

