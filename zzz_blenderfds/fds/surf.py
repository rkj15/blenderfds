"""BlenderFDS, FDS SURF routines"""

import bpy

predefined = ("INERT", "OPEN", "MIRROR")

def has_predefined():
    """Check predefined materials"""
    return set(predefined) <= set(bpy.data.materials.keys())

def set_predefined(context):
    """Set BlenderFDS predefined materials/bcs"""
    mas = bpy.data.materials.keys()
    value = str()
    if "INERT" not in mas:  value += "&SURF ID='INERT'  RGB=204,204,51 FYI='Predefined SURF' /\n"
    if "OPEN" not in mas:   value += "&SURF ID='OPEN'   RGB=51,204,204 FYI='Predefined SURF' TRANSPARENCY=.2 /\n"
    if "MIRROR" not in mas: value += "&SURF ID='MIRROR' RGB=51,51,204  FYI='Predefined SURF' /\n"
    if value: context.scene.from_fds(context, value)
