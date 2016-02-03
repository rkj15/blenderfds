"""BlenderFDS, FDS HEAD routines"""

import bpy

DEBUG = False

def set_free_text_file(context, scene):
    """Get or set unique free text file name, open it in shown Blender Text Editor area."""
    # Name?
    if not scene.bf_head_free_text:
        # No free text name, find and set unique name
        bf_head_free_text = bf_head_free_text_new = "HEAD free text"
        i = 0
        while bf_head_free_text_new in bpy.data.texts:
            i += 1
            bf_head_free_text_new = ".".join((bf_head_free_text, str(i)))
        scene.bf_head_free_text = bf_head_free_text_new
    # File?
    if not scene.bf_head_free_text in bpy.data.texts:
        # No file: create file
        bpy.data.texts.new(scene.bf_head_free_text)
    # Search for the Text Editor area in Blender UI. If found, show requested text
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'TEXT_EDITOR':
                area.spaces[0].text = bpy.data.texts[scene.bf_head_free_text]
                break
    # Return free text file name
    return scene.bf_head_free_text
    
