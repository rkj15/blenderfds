"""BlenderFDS, Blender handlers, manage file version and conversions to new format"""

import bpy

from .. import fds
from .. import config

DEBUG = False

### Register/Unregister

def register():
    """Register handlers"""
    DEBUG and print("BFDS: handlers.py register")
    bpy.app.handlers.load_post.append(_load_post)
    bpy.app.handlers.save_pre.append(_save_pre)

def unregister():
    """Unregister handlers"""
    DEBUG and print("BFDS: handlers.py unregister")
    bpy.app.handlers.load_post.append(_load_post)
    bpy.app.handlers.save_pre.append(_save_pre)


### Definitions

@bpy.app.handlers.persistent
def _load_post(self):
    """This function is run after each time a Blender file is loaded"""
    # Check file format version
    check_file_version(bpy.context)
    # Init FDS default materials
    if not fds.surf.has_predefined(): bpy.ops.material.bf_set_predefined()
    # Set default scene appearance
    for scene in bpy.data.scenes: scene.set_default_appearance(context=None)
    # Open the right file in editor
    context = bpy.context
    fds.head.set_free_text_file(context, context.scene)
    
@bpy.app.handlers.persistent
def _save_pre(self):
    """This function is run before each time a Blender file is saved"""
    # Set file format version
    set_file_version(bpy.context)


### Manage file version and conversion to new formats

def get_file_version(context):
    file_version = context.scene.bf_file_version
    # This is an hack. No way to detect old files...
    for ob in bpy.data.objects[:10]: # Check first objects only
        if ob.bf_nl: # Check if an old namelist is set
            for ob in bpy.data.objects: ob.bf_nl = str() # Clear it  
            return 0,0,0 # This file is older than 2.0.1
        else: file_version = tuple(context.scene.bf_file_version)
    return file_version

def get_file_version_string(context):
    file_version = get_file_version(context)
    return file_version[0] and "{0[0]}.{0[1]}.{0[2]}".format(file_version) or "<2.0.1"

def check_file_version(context):
    """Check current file version and manage eventual conversion."""
    # Init
    file_version = tuple(get_file_version(context))
    file_version_string = get_file_version_string(context)
    print("BFDS: File version:", file_version_string)
    # Protect the following bf_dialog operator, if Blender is still not ready to show it
    if not context.window: return
    # Check older
    if  file_version < (4,0,0): # Check latest file format change
        msg = "Check your old input data!"
        description = \
"""This file was created on BlenderFDS {}.
Automatic data conversion to current BlenderFDS
and FDS format is not supported.""".format(file_version_string)
        bpy.ops.wm.bf_dialog('INVOKE_DEFAULT', msg=msg, description=description, type="ERROR")
    # Check newer
    elif file_version > config.supported_file_version:
        msg = "Install BlenderFDS {} for full support of your data!".format(file_version_string)
        description = \
"""This file was created on BlenderFDS {}.
You are currently using an older version,
new features are not supported.""".format(file_version_string)
        bpy.ops.wm.bf_dialog('INVOKE_DEFAULT', msg=msg, description=description, type="ERROR")

def set_file_version(context):
    """Set current file version."""
    for sc in bpy.data.scenes: sc.bf_file_version = config.supported_file_version

