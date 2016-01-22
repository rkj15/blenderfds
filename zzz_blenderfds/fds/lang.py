"""BlenderFDS, fds language"""

import re, os.path

import bpy
from bpy.types import Scene, Object, Material
from bpy.props import *

from ..types import *
from .. import geometry
from . import tables, mesh

from .. import config

DEBUG = False

# TODO: evacuation namelists

### System

# Object related namelist cls name

def update_OP_namelist_cls(self, context):
    # Del all tmp_objects, if self has one
    if self.bf_has_tmp: geometry.tmp_objects.del_all(context)
    # Check allowed geometries, different namelists may have different allowed geometries
    bf_namelist = self.bf_namelist
    bf_prop_XB = bf_namelist.bf_prop_XB
    bf_prop_XYZ = bf_namelist.bf_prop_XYZ    
    bf_prop_PB = bf_namelist.bf_prop_PB 
    if bf_prop_XB and self.bf_xb not in bf_prop_XB.allowed_items: self.bf_xb = "NONE"
    if bf_prop_XYZ and self.bf_xyz not in bf_prop_XYZ.allowed_items: self.bf_xyz = "NONE"
    if bf_prop_PB and self.bf_pb not in bf_prop_PB.allowed_items: self.bf_pb = "NONE"
    # Set default appearance
    self.set_default_appearance(context)

@subscribe
class OP_namelist_cls(BFProp):
    label = "Namelist cls"
    description = "Identification of FDS namelist cls"
    bpy_type = Object
    bpy_idname = "bf_namelist_cls"
    bpy_prop = EnumProperty
    bpy_default = "ON_OBST"
    bpy_other = {
        "items": (("ON_OBST", "OBST", "Obstruction", 1000),),
        "update": update_OP_namelist_cls,
    }

# Material related namelist cls name

def update_MP_namelist_cls(self, context):
    # Set default appearance
    self.set_default_appearance(context)

@subscribe
class MP_namelist_cls(BFProp):
    label = "Namelist cls"
    description = "Identification of FDS namelist"
    bpy_type = Material
    bpy_idname = "bf_namelist_cls"
    bpy_prop = EnumProperty
    bpy_default = "MN_SURF"
    bpy_other = {
        "items": (("MN_SURF", "SURF", "Generic boundary condition", 2000),),
        "update": update_MP_namelist_cls
    }

# Object tmp

@subscribe
class OP_is_tmp(BFProp):
    label = "Is Tmp"
    description = "Set if this element is tmp"
    bpy_type = Object
    bpy_idname = "bf_is_tmp"
    bpy_prop = BoolProperty
    bpy_default = False

@subscribe
class OP_has_tmp(BFProp):
    label = "Has Tmp"
    description = "Set if this element has a tmp element companion"
    bpy_type = Object
    bpy_idname = "bf_has_tmp"
    bpy_prop = BoolProperty
    bpy_default = False

# File version

@subscribe
class SP_file_version(BFProp):
    label = "BlenderFDS File Version"
    description = "BlenderFDS file format version"
    bpy_type = Scene
    bpy_idname = "bf_file_version"
    bpy_prop = IntVectorProperty
    bpy_default = config.supported_file_version
    bpy_other = {"size":3,}

# Old object properties from old BlenderFDS to allow transition

@subscribe
class OP_namelist_old_1(BFStringProp):
    label = "Old Namelist 1"
    description = "Old type of FDS namelist 1"
    bpy_type = Object
    bpy_idname = "bf_nl"


### Geometric props

# Voxel/Pixel size

def update_bf_xb_voxel_size(self, context):
    """Update function for bf_xb_voxel_size"""
    geometry.tmp_objects.del_all(context)

@subscribe
class OP_XB_precise_bbox(BFNoAutoUIMod, BFNoAutoExportMod, BFProp):
    label = "Precise positioning"
    description = "Center voxels/pixels to original bounding box"
    bpy_type = Object
    bpy_idname = "bf_xb_precise_bbox"
    bpy_prop = BoolProperty
    bpy_default = False
    bpy_other = {
        "update": update_bf_xb_voxel_size
    }

@subscribe
class OP_XB_custom_voxel(BFNoAutoUIMod, BFNoAutoExportMod, BFProp):
    label = "Use custom settings"
    description = "Use custom settings for object voxelization/pixelization"
    bpy_type = Object
    bpy_idname = "bf_xb_custom_voxel"
    bpy_prop = BoolProperty
    bpy_default = False
    bpy_other = {
        "update": update_bf_xb_voxel_size
    }

@subscribe
class OP_XB_voxel_size(BFNoAutoUIMod, BFNoAutoExportMod, BFProp):
    label = "Resolution"
    description = "Resolution for object voxelization/pixelization"
    bpy_type = Object
    bpy_idname = "bf_xb_voxel_size"
    bpy_prop = FloatProperty
    bpy_default = .10
    bpy_other =  {
        "step": 1.,
        "precision": 3,
        "min": .001,
        "max": 20.,
        "update": update_bf_xb_voxel_size
    }
    # unit = "LENGTH", # correction for scale_length needed before exporting!

@subscribe
class SP_default_voxel_size(BFNoAutoExportMod, BFProp):
    label = "Default Resolution"
    description = "Default resolution for object voxelization/pixelization"
    bpy_type = Scene
    bpy_idname = "bf_default_voxel_size"
    bpy_prop = FloatProperty
    bpy_default = .10
    bpy_other =  {
        "step": 1.,
        "precision": 3,
        "min": .001,
        "max": 20.,
        "update": update_bf_xb_voxel_size
    }
    # unit = "LENGTH", # correction for scale_length needed before exporting!

# XB

def update_bf_xb(self, context):
    """Update function for bf_xb"""
    # Del all tmp_objects, if self has one
    if self.bf_has_tmp: geometry.tmp_objects.del_all(context)
    # Set other geometries to compatible settings
    if self.bf_xb in ("VOXELS", "FACES", "PIXELS", "EDGES"):
        if self.bf_xyz == "VERTICES": self.bf_xyz = "NONE"
        if self.bf_pb == "PLANES": self.bf_pb = "NONE"

@subscribe
class OP_XB(BFXBProp):
    bf_props = OP_XB_precise_bbox, OP_XB_custom_voxel, OP_XB_voxel_size
    bpy_default = "BBOX"
    bpy_other = {
        "update": update_bf_xb,
        "items": (
            ("NONE", "None", "Not exported", 0),
            ("BBOX", "BBox", "Use object bounding box", 100),
            ("VOXELS", "Voxels", "Export voxels from voxelized solid object", 200),
            ("FACES", "Faces", "Faces, one for each face of this object", 300),
            ("PIXELS", "Pixels", "Export pixels from pixelized flat object", 400),
            ("EDGES", "Edges", "Segments, one for each edge of this object", 500),
        )
    }
    allowed_items = "NONE", "BBOX", "VOXELS", "FACES", "PIXELS", "EDGES"

    def _draw_body(self, context, layout):
        super()._draw_body(context, layout)
        if not self.element.bf_xb in ("VOXELS", "PIXELS"): return
        # Draw VOXELS, PIXELS properties
        row = layout.row()
        row.prop(self.element, "bf_xb_precise_bbox")
        layout_export, layout_custom = row.column(), row.column()
        layout_export.prop(self.element, "bf_xb_custom_voxel", text="")
        row = layout_custom.row(align=True)
        row.prop(self.element, "bf_xb_voxel_size")
        layout_custom.active = self.element.bf_xb_custom_voxel

    def _format_xb(self, value):
        return "XB={0[0]:.3f},{0[1]:.3f},{0[2]:.3f},{0[3]:.3f},{0[4]:.3f},{0[5]:.3f}".format(value)

    def _format_xb_idi(self, value, name, i):
        return "ID='{1}_{2}'\n      XB={0[0]:.3f},{0[1]:.3f},{0[2]:.3f},{0[3]:.3f},{0[4]:.3f},{0[5]:.3f}".format(value, name, i)

    def _format_xb_idx(self, value, name, i):
        return "ID='{1}{0[0]:+.3f}'\n      XB={0[0]:.3f},{0[1]:.3f},{0[2]:.3f},{0[3]:.3f},{0[4]:.3f},{0[5]:.3f}".format(value, name)

    def _format_xb_idy(self, value, name, i):
        return "ID='{1}{0[2]:+.3f}'\n      XB={0[0]:.3f},{0[1]:.3f},{0[2]:.3f},{0[3]:.3f},{0[4]:.3f},{0[5]:.3f}".format(value, name)

    def _format_xb_idz(self, value, name, i):
        return "ID='{1}{0[4]:+.3f}'\n      XB={0[0]:.3f},{0[1]:.3f},{0[2]:.3f},{0[3]:.3f},{0[4]:.3f},{0[5]:.3f}".format(value, name)

    def _format_xb_idxy(self, value, name, i):
        return "ID='{1}{0[0]:+.3f}{0[2]:+.3f}'\n      XB={0[0]:.3f},{0[1]:.3f},{0[2]:.3f},{0[3]:.3f},{0[4]:.3f},{0[5]:.3f}".format(value, name)

    def _format_xb_idxz(self, value, name, i):
        return "ID='{1}{0[0]:+.3f}{0[4]:+.3f}'\n      XB={0[0]:.3f},{0[1]:.3f},{0[2]:.3f},{0[3]:.3f},{0[4]:.3f},{0[5]:.3f}".format(value, name)

    def _format_xb_idyz(self, value, name, i):
        return "ID='{1}{0[2]:+.3f}{0[4]:+.3f}'\n      XB={0[0]:.3f},{0[1]:.3f},{0[2]:.3f},{0[3]:.3f},{0[4]:.3f},{0[5]:.3f}".format(value, name)

    def _format_xb_idxyz(self, value, name, i):
        return "ID='{1}{0[0]:+.3f}{0[2]:+.3f}{0[4]:+.3f}'\n      XB={0[0]:.3f},{0[1]:.3f},{0[2]:.3f},{0[3]:.3f},{0[4]:.3f},{0[5]:.3f}".format(value, name)
    
    def to_fds(self, context):
        # Check
        self.check(context)
        # Init
        bf_xb = self.element.bf_xb
        if bf_xb not in self.allowed_items: return None
        # Get coordinates
        xbs, msg = geometry.to_fds.ob_to_xbs(context, self.element)
        if msg: self.infos.append(msg)
        if not xbs: return None     
        # Correct for scale_lenght
        scale_length = context.scene.unit_settings.scale_length
        xbs = [[coo * scale_length for coo in xb] for xb in xbs]
        # Prepare
        if len(xbs) == 1:
            return self._format_xb(xbs[0])
        else:
            _format_xb = {
                "IDI" :   self._format_xb_idi,
                "IDX" :   self._format_xb_idx,
                "IDY" :   self._format_xb_idy,
                "IDZ" :   self._format_xb_idz,
                "IDXY" :  self._format_xb_idxy,
                "IDXZ" :  self._format_xb_idxz,
                "IDYZ" :  self._format_xb_idyz,
                "IDXYZ" : self._format_xb_idxyz,
            }[self.element.bf_id_suffix]
            name = self.element.name
            return [_format_xb(xb, name, i) for i, xb in enumerate(xbs)]

    def from_fds(self, context, value):
        try:
            # Correct for scale_lenght
            scale_length = context.scene.unit_settings.scale_length
            value = [coo / scale_length for coo in value]
            # Set value
            geometry.from_fds.xbs_to_ob(
                xbs=(value,),
                context=context,
                ob=self.element,
                bf_xb=self.element.bf_xb
            ) # Send existing element.bf_xb for evaluation.
        # TODO: EDGE recognition!
        except: raise BFException(self, "Error in setting '{}' value".format(value))# FIXME test        
        
@subscribe
class OP_XB_bbox(OP_XB):
    allowed_items = "NONE", "BBOX"

@subscribe
class OP_XB_solid(OP_XB):
    allowed_items = "NONE", "BBOX", "VOXELS"

@subscribe
class OP_XB_faces(OP_XB):
    allowed_items = "NONE", "FACES", "PIXELS"

# XYZ

def update_bf_xyz(self, context):
    """Update function for bf_xyz"""
    # Del all tmp_objects, if self has one
    if self.bf_has_tmp: geometry.tmp_objects.del_all(context)
    # Set other geometries to compatible settings
    if self.bf_xyz == "VERTICES":
        if self.bf_xb in ("VOXELS", "FACES", "PIXELS", "EDGES"): self.bf_xb = "NONE"
        if self.bf_pb == "PLANES": self.bf_pb = "NONE"

@subscribe
class OP_XYZ(BFXYZProp):
    bpy_prop = EnumProperty
    bpy_default = "NONE"
    bpy_other = {
        "update": update_bf_xyz,
        "items": (
            ("NONE", "None", "Not exported", 0),
            ("CENTER", "Center", "Point, corresponding to the center point of this object", 100),
            ("VERTICES", "Vertices", "Points, one for each vertex of this object", 200),
        )
    }

    allowed_items = "NONE", "CENTER", "VERTICES"

    def _format_xyz(self, value):
        return "XYZ={0[0]:.3f},{0[1]:.3f},{0[2]:.3f}".format(value)

    def _format_xyz_idi(self, value, name, i):
        return "ID='{1}_{2}'\n      XYZ={0[0]:.3f},{0[1]:.3f},{0[2]:.3f}".format(value, name, i)

    def _format_xyz_idx(self, value, name, i):
        return "ID='{1}{0[0]:+.3f}'\n      XYZ={0[0]:.3f},{0[1]:.3f},{0[2]:.3f}".format(value, name)

    def _format_xyz_idy(self, value, name, i):
        return "ID='{1}{0[1]:+.3f}'\n      XYZ={0[0]:.3f},{0[1]:.3f},{0[2]:.3f}".format(value, name)

    def _format_xyz_idz(self, value, name, i):
        return "ID='{1}{0[2]:+.3f}'\n      XYZ={0[0]:.3f},{0[1]:.3f},{0[2]:.3f}".format(value, name)

    def _format_xyz_idxy(self, value, name, i):
        return "ID='{1}{0[0]:+.3f}{0[1]:+.3f}'\n      XYZ={0[0]:.3f},{0[1]:.3f},{0[2]:.3f}".format(value, name)

    def _format_xyz_idxz(self, value, name, i):
        return "ID='{1}{0[0]:+.3f}{0[2]:+.3f}'\n      XYZ={0[0]:.3f},{0[1]:.3f},{0[2]:.3f}".format(value, name)

    def _format_xyz_idyz(self, value, name, i):
        return "ID='{1}{0[1]:+.3f}{0[2]:+.3f}'\n      XYZ={0[0]:.3f},{0[1]:.3f},{0[2]:.3f}".format(value, name)

    def _format_xyz_idxyz(self, value, name, i):
        return "ID='{1}{0[0]:+.3f}{0[1]:+.3f}{0[2]:+.3f}'\n      XYZ={0[0]:.3f},{0[1]:.3f},{0[2]:.3f}".format(value, name)

    def to_fds(self, context):
        # Check
        self.check(context)
        # Init
        bf_xyz = self.element.bf_xyz
        if bf_xyz not in self.allowed_items: return None
        # Get coordinates
        xyzs, msg = geometry.to_fds.ob_to_xyzs(context, self.element)
        if msg: self.infos.append(msg)
        if not xyzs: return None
        # Correct for scale_lenght
        scale_length = context.scene.unit_settings.scale_length
        xyzs = [[coo * scale_length for coo in xyz] for xyz in xyzs]
        # Prepare
        if len(xyzs) == 1:
            return self._format_xyz(xyzs[0])
        else:
            _format_xyz = {
                "IDI" :   self._format_xyz_idi,
                "IDX" :   self._format_xyz_idx,
                "IDY" :   self._format_xyz_idy,
                "IDZ" :   self._format_xyz_idz,
                "IDXY" :  self._format_xyz_idxy,
                "IDXZ" :  self._format_xyz_idxz,
                "IDYZ" :  self._format_xyz_idyz,
                "IDXYZ" : self._format_xyz_idxyz,
            }[self.element.bf_id_suffix]
            name = self.element.name
            return [_format_xyz(xyz, name, i) for i, xyz in enumerate(xyzs)]

    def from_fds(self, context, value):
        try:
            # Correct for scale_lenght
            scale_length = context.scene.unit_settings.scale_length
            value = [coo / scale_length for coo in value]
            # Set value
            geometry.from_fds.xyzs_to_ob(
                xyzs=(value,),
                context=context,
                ob=self.element,
                bf_xyz=self.element.bf_xyz
            ) # Send existing self.element.bf_xyz for evaluation
        except: raise BFException(self, "Error in setting '{}' value".format(value))# FIXME test        

# PB

def update_bf_pb(self, context):
    """Update function for bf_pb"""
    # Del all tmp_objects
    if self.bf_has_tmp: geometry.tmp_objects.del_all(context)
    # Set other geometries to compatible settings
    if self.bf_pb == "PLANES":
        if self.bf_xb in ("VOXELS", "FACES", "PIXELS", "EDGES"): self.bf_xb = "NONE"
        if self.bf_xyz == "VERTICES": self.bf_xyz = "NONE"

# @subscribe OP_PB later, because OP_PB* are defined later
# if not dependent on OP_PB they are not registered
class OP_PB(BFPBProp):
    # bf_props = OP_PBX, OP_PBY, OP_PBZ are defined later
    bpy_prop = EnumProperty
    bpy_default = "NONE"
    bpy_other = {
        "update": update_bf_pb,
        "items": (
            ("NONE", "None", "Not exported", 0),
            ("PLANES", "Planes", "Planes, one for each face of this object", 100),
        )
    }

    allowed_items = "NONE", "PLANES"

    def _format_pb(self, value):
        return "PB{0[0]}={0[1]:.3f}".format(value)

    def _format_pb_idi(self, value, name, i):
        return "ID='{1}_{2}'\n      PB{0[0]}={0[1]:.3f}".format(value, name, i)

    def _format_pb_idxyz(self, value, name, i):
        return "ID='{1}_{0[0]}{0[1]:+.3f}'\n      PB{0[0]}={0[1]:.3f}".format(value, name)

    def to_fds(self, context):
        # Check
        self.check(context)
        # Init
        bf_pb = self.element.bf_pb
        if bf_pb not in self.allowed_items: return None
        # Get coordinates
        pbs, msg = geometry.to_fds.ob_to_pbs(context, self.element)
        if msg: self.infos.append(msg)
        if not pbs: return None
        # Correct for scale_lenght
        scale_length = context.scene.unit_settings.scale_length
        pbs = [[pb[0], pb[1] * scale_length] for pb in pbs]
        # Prepare
        if len(pbs) == 1:
            return self._format_pb(pbs[0])
        else:
            _format_pb = {
                "IDI" :   self._format_pb_idi,
                "IDX" :   self._format_pb_idxyz,
                "IDY" :   self._format_pb_idxyz,
                "IDZ" :   self._format_pb_idxyz,
                "IDXY" :  self._format_pb_idxyz,
                "IDXZ" :  self._format_pb_idxyz,
                "IDYZ" :  self._format_pb_idxyz,
                "IDXYZ" : self._format_pb_idxyz,
            }[self.element.bf_id_suffix]
            name = self.element.name
            return [_format_pb(pb, name, i) for i, pb in enumerate(pbs)]

    def from_fds(self, context, value):
        try:
            # Correct for scale_lenght
            value = value / context.scene.unit_settings.scale_length
            # Set value
            pbs = ((self.fds_label[2], value),) # eg: (("X", 3.4),)
            geometry.from_fds.pbs_to_ob(
                pbs=pbs,
                context=context,
                ob=self.element,
                bf_pb=self.element.bf_pb
            ) # Send existing self.element.bf_pb for evaluation
        except: raise BFException(self, "Error in setting '{}' value".format(value))# FIXME test        


@subscribe
class OP_PBX(BFNoAutoUIMod, BFNoAutoExportMod, OP_PB): # used for PBX, PBY, PBZ import trapping
    label = "PBX"
    bf_props = []
    fds_label = "PBX"

@subscribe
class OP_PBY(BFNoAutoUIMod, BFNoAutoExportMod, OP_PB): # used for PBX, PBY, PBZ import trapping
    label = "PBY"
    bf_props = []
    fds_label = "PBY"

@subscribe
class OP_PBZ(BFNoAutoUIMod, BFNoAutoExportMod, OP_PB): # used for PBX, PBY, PBZ import trapping
    label = "PBZ"
    bf_props = []
    fds_label = "PBZ"

# now OP_PB* are defined,
# we can update OP_PB.bf_props and subscribe OP_PB
OP_PB.bf_props = OP_PBX, OP_PBY, OP_PBZ
subscribe(OP_PB)

### Scene namelists and their specific properties

# HEAD

@subscribe
class SP_HEAD_CHID(BFStringProp):
    label = "CHID"
    description = "Case identificator"
    overwrite = False # Do not allow replacement
    fds_label = "CHID"
    bpy_type = Scene
    bpy_prop = None # Do not register
    bpy_idname = "name"

    def _draw_body(self, context, layout):
        row = layout.row()
        row.template_ID(context.screen, "scene", new="scene.new", unlink="scene.delete")

    def check(self, context):
        value = self.element.name
        if value and bpy.path.clean_name(value) != value:
            raise BFException(self, "Illegal characters in case filename")

@subscribe
class SP_HEAD_TITLE(BFStringProp):
    label = "TITLE"
    description = "Case description"
    overwrite = False # Do not allow replacement
    fds_label = "TITLE"
    bpy_type = Scene
    bpy_idname = "bf_head_title"
    bpy_default = ""
    bpy_other =  {"maxlen": 64,}

@subscribe
class SP_HEAD_directory(BFNoAutoExportMod, BFProp):
    label = "Case Directory"
    description = "Case directory"
    overwrite = False # Do not allow replacement
    bpy_type = Scene
    bpy_idname = "bf_head_directory"
    bpy_prop = StringProperty
    bpy_default = ""
    bpy_other =  {"subtype": "DIR_PATH", "maxlen": 1024,}

    def check(self, context):
        value = self.element.bf_head_directory
        if value and not os.path.exists(bpy.path.abspath(value)):
            raise BFException(self, "Case directory path not existing")

@subscribe
class SP_HEAD_free_text(BFNoAutoExportMod, BFProp):
    label = "Free Text File"
    description = "Name of the free text file appended to the HEAD namelist"
    overwrite = False # Do not allow replacement
    bpy_type = Scene
    bpy_idname = "bf_head_free_text"
    bpy_prop = StringProperty
    bpy_default = ""

    def _draw_body(self, context, layout):
        row = layout.row(align=True)
        row.prop_search(self.element, self.bpy_idname, bpy.data, "texts")
        row.operator("scene.bf_edit_head_free_text", icon="GREASEPENCIL", text="")

    def check(self, context):
        bf_head_free_text = self.element.bf_head_free_text
        if not bf_head_free_text: return None
        # Check existence
        if bf_head_free_text not in bpy.data.texts:
            raise BFException(self, "Free text file not existing")

@subscribe
class SN_HEAD(BFNamelist):
    label = "HEAD"
    description = "FDS case header"
    overwrite = False # Do not allow replacement
    enum_id = 3001
    fds_label = "HEAD"
    bpy_type = Scene
    bf_props = SP_HEAD_CHID, SP_HEAD_TITLE, SP_HEAD_directory, SP_default_voxel_size, SP_HEAD_free_text

# TIME

@subscribe
class SP_TIME_export(BFExportProp):
    description = "Set if TIME namelist is exported to FDS"
    bpy_type = Scene
    bpy_idname = "bf_time_export"
    bpy_default = True

@subscribe
class SP_TIME_T_BEGIN(BFProp):
    label = "T_BEGIN [s]"
    description = "Simulation starting time"
    fds_label = "T_BEGIN"
    bpy_type = Scene
    bpy_idname = "bf_time_t_begin"
    bpy_prop = FloatProperty
    bpy_default = 0.
    bpy_other = {
        "unit": "TIME",
        "step": 100.,
        "precision": 1,
        "min": 0.
    }

    def get_exported(self, context):
        return not self.element.bf_time_setup_only

@subscribe
class SP_TIME_T_END(SP_TIME_T_BEGIN):
    label = "T_END [s]"
    description = "Simulation ending time"
    fds_label = "T_END"
    bpy_idname = "bf_time_t_end"

@subscribe
class SP_TIME_setup_only(BFProp):
    label = "Smokeview Geometry Setup"
    description = "Smokeview geometry setup"
    bpy_type = Scene
    bpy_idname = "bf_time_setup_only"
    bpy_prop = BoolProperty
    bpy_default = True

    def to_fds(self, context):
        if self.element.bf_time_setup_only: return "T_END=0."

@subscribe
class SP_TIME_free(BFFreeProp):
    bpy_type = Scene
    bpy_idname = "bf_time_free"

@subscribe
class SN_TIME(BFNamelist):
    label = "TIME"
    description = "Simulation time settings"
    enum_id = 3002
    fds_label = "TIME"
    bf_prop_export = SP_TIME_export
    bpy_type = Scene
    bf_props = SP_TIME_T_BEGIN, SP_TIME_T_END, SP_TIME_setup_only, SP_TIME_free


# MISC

@subscribe
class SP_MISC_export(BFExportProp):
    description = "Set if MISC namelist is exported to FDS"
    bpy_type = Scene
    bpy_idname = "bf_misc_export"

@subscribe
class SP_MISC_FYI(BFFYIProp):
    bpy_type = Scene
    bpy_idname = "bf_misc_fyi"

    def _draw_body(self, context, layout):
        row = layout.row()
        row.prop(self.element, self.bpy_idname, text="", icon="INFO")
        row.operator("scene.bf_load_misc", icon="LOAD_FACTORY", text="")

@subscribe
class SP_MISC_free(BFFreeProp):
    bpy_type = Scene
    bpy_idname = "bf_misc_free"

@subscribe
class SN_MISC(BFNamelist):
    label = "MISC"
    description = "Miscellaneous parameters"
    enum_id = 3003
    fds_label = "MISC"
    bf_prop_export = SP_MISC_export
    bpy_type = Scene
    bf_props = SP_MISC_FYI, SP_MISC_free
    

# REAC

@subscribe
class SP_REAC_export(BFExportProp):
    description = "Set if REAC namelist is exported to FDS"
    bpy_type = Scene
    bpy_idname = "bf_reac_export"

@subscribe
class SP_REAC_FUEL(BFStringProp):
    label = "FUEL"
    description = "Identificator of fuel species"
    fds_label = "FUEL"
    bpy_type = Scene
    bpy_idname = "bf_reac_fuel"

    def _draw_body(self, context, layout):
        row = layout.row()
        row.prop(self.element, "bf_reac_fuel")
        row.operator("scene.bf_load_reac", icon="LOAD_FACTORY", text="")

@subscribe
class SP_REAC_FYI(BFFYIProp):
    bpy_type = Scene
    bpy_idname = "bf_reac_fyi"

@subscribe
class SP_REAC_FORMULA_export(BFExportProp):
    bpy_type = Scene
    bpy_idname = "bf_reac_formula_export"

@subscribe
class SP_REAC_FORMULA(BFStringProp):
    label = "FORMULA"
    description = "Chemical formula of fuel species, it can only contain C, H, O, or N"
    fds_label = "FORMULA"
    bf_prop_export = SP_REAC_FORMULA_export
    bpy_type = Scene
    bpy_idname = "bf_reac_formula"

@subscribe
class SP_REAC_CO_YIELD_export(BFExportProp):
    bpy_type = Scene
    bpy_idname = "bf_reac_co_yield_export"

@subscribe
class SP_REAC_CO_YIELD(BFProp):
    label = "CO_YIELD [kg/kg]"
    description = "Fraction of fuel mass converted into carbon monoxide"
    fds_label = "CO_YIELD"
    bf_prop_export = SP_REAC_CO_YIELD_export
    bpy_type = Scene
    bpy_idname = "bf_reac_co_yield"
    bpy_prop = FloatProperty
    bpy_default = 0.
    bpy_other = {
        "step": 1.,
        "precision": 3,
        "min": 0.,
        "max": 1.,
    }

@subscribe
class SP_REAC_SOOT_YIELD_export(BFExportProp):
    bpy_type = Scene
    bpy_idname = "bf_reac_soot_yield_export"

@subscribe
class SP_REAC_SOOT_YIELD(SP_REAC_CO_YIELD):
    label = "SOOT_YIELD [kg/kg]"
    description = "Fraction of fuel mass converted into smoke particulate"
    fds_label = "SOOT_YIELD"
    bf_prop_export = SP_REAC_SOOT_YIELD_export
    bpy_type = Scene
    bpy_idname = "bf_reac_soot_yield"

@subscribe
class SP_REAC_HEAT_OF_COMBUSTION_export(BFExportProp):
    bpy_type = Scene
    bpy_idname = "bf_reac_heat_of_combustion_export"

@subscribe
class SP_REAC_HEAT_OF_COMBUSTION(BFProp):
    label = "HEAT_OF_COMBUSTION [kJ/kg]"
    description = "Fuel heat of combustion"
    fds_label = "HEAT_OF_COMBUSTION"
    bf_prop_export = SP_REAC_HEAT_OF_COMBUSTION_export
    bpy_type = Scene
    bpy_idname = "bf_reac_heat_of_combustion"
    bpy_prop = FloatProperty
    bpy_default = 0.
    bpy_other = {
        "step": 100000.,
        "precision": 1,
        "min": 0.,
    }

@subscribe
class SP_REAC_IDEAL(BFBoolProp):
    label = "IDEAL"
    description = "Set ideal heat of combustion to .TRUE."
    fds_label = "IDEAL"
    bpy_type = Scene
    bpy_idname = "bf_reac_ideal"
    bpy_default = False

@subscribe
class SP_REAC_free(BFFreeProp):
    bpy_type = Scene
    bpy_idname = "bf_reac_free"

@subscribe
class SN_REAC(BFNamelist):
    label = "REAC"
    description = "Reaction"
    enum_id = 3004
    fds_label = "REAC"
    bf_prop_export = SP_REAC_export
    bf_props = SP_REAC_FUEL, SP_REAC_FYI, SP_REAC_FORMULA, SP_REAC_CO_YIELD, SP_REAC_SOOT_YIELD, SP_REAC_HEAT_OF_COMBUSTION, SP_REAC_IDEAL, SP_REAC_free
    bpy_type = Scene


# DUMP

@subscribe
class SP_DUMP_export(BFExportProp):
    description = "Set if DUMP namelist is exported to FDS"
    bpy_type = Scene
    bpy_idname = "bf_dump_export"
    bpy_default = True

@subscribe
class SP_DUMP_render_file(BFProp):
    label = "Export Geometric Description File"
    description = "Export geometric description file GE1"
    fds_label = "RENDER_FILE"
    bpy_type = Scene
    bpy_idname = "bf_dump_render_file"
    bpy_prop = BoolProperty
    bpy_default = True

    def to_fds(self, context):
        if self.element.bf_dump_render_file: return "RENDER_FILE='{}.ge1'".format(self.element.name)

    def from_fds(self, context, value): # In FDS this parameter contains a string, here it is a bool
        if value: super().from_fds(context, True)
        else: super().from_fds(context, False)

@subscribe
class SP_DUMP_NFRAMES_export(BFExportProp):
    bpy_type = Scene
    bpy_idname = "bf_dump_nframes_export"

@subscribe
class SP_DUMP_NFRAMES(BFProp):
    label = "NFRAMES"
    description = "Number of output dumps per calculation"
    fds_label = "NFRAMES"
    bf_prop_export = SP_DUMP_NFRAMES_export
    bpy_type = Scene
    bpy_idname = "bf_dump_nframes"
    bpy_prop = IntProperty
    bpy_default = 1000
    bpy_other = {"min": 1}

    def check(self, context):
        self.infos.append("Output is dumped every {:.2f} s".format(
            (self.element.bf_time_t_end - self.element.bf_time_t_begin) / self.element.bf_dump_nframes
        ))  # bf_dump_nframes != 0, its min is 1

@subscribe
class SP_DUMP_free(BFFreeProp):
    bpy_type = Scene
    bpy_idname = "bf_dump_free"

@subscribe
class SN_DUMP(BFNamelist):
    label = "DUMP"
    description = "Output parameters"
    enum_id = 3005
    fds_label = "DUMP"
    bf_prop_export = SP_DUMP_export
    bf_props = SP_DUMP_render_file, SP_DUMP_NFRAMES, SP_DUMP_free
    bpy_type = Scene


# TAIL

@subscribe
class SN_TAIL(BFNoAutoUIMod, BFNoAutoExportMod, BFNamelist):
    label = "TAIL"
    enum_id = 3100
    fds_label = "TAIL"
    bpy_type = Scene


### Material namelists and their specific properties

@subscribe
class MP_export(BFExportProp):
    bpy_type = Material
    bpy_default = False

@subscribe
class MP_ID(BFStringProp):
    label = "ID"
    description = "Material identificator"
    overwrite = False # Do not allow replacement
    fds_label = "ID"
    bpy_type = Material
    bpy_prop = None # Do not register
    bpy_idname = "name"

    def _draw_body(self, context, layout):
        row = layout.row()
        row.template_ID(context.object, "active_material", new="material.new")
        row.operator("material.bf_load_surf", icon="LOAD_FACTORY", text="")

@subscribe
class MP_FYI(BFFYIProp):
    bpy_type = Material

@subscribe
class MP_free(BFFreeProp):
    bpy_type = Material

@subscribe
class MP_COLOR(BFNoAutoUIMod, BFNoAutoExportMod, BFProp): # For COLOR trapping during import only
    label = "Color"
    description = "Color"
    fds_label = "COLOR"
    bpy_type = Material
    bpy_prop = None # Do not register
    bpy_idname = "diffuse_color"

    def from_fds(self, context, value): # FIXME test
        try: value = tables.colors[value]
        except KeyError: raise BFException(self, "Unknown color name '{}'".format(value))
        self.element.diffuse_color = value[0]/255, value[1]/255, value[2]/255

@subscribe
class MP_RGB(BFNoAutoUIMod, BFProp): # ui is statically added in the material panel
    label = "RGB"
    description = "A triplet of integer color values (red, green, blue)"
    fds_label = "RGB"
    bf_props = MP_COLOR, # call bf_color for registration
    bpy_type = Material
    bpy_prop = None # Do not register
    bpy_idname = "diffuse_color"

    def to_fds(self, context): # FIXME test
        color = self.element.diffuse_color
        return "RGB={},{},{}".format(int(color[0]*255), int(color[1]*255), int(color[2]*255))   

#    def get_value(self):
#        color = self.element.diffuse_color
#        return int(color[0]*255), int(color[1]*255), int(color[2]*255)

    def from_fds(self, context, value):
        try: self.element.diffuse_color = value[0]/255, value[1]/255, value[2]/255
        except: raise BFException(self, "Wrong RGB color value '{}'".format(value))

#    def set_value(self, context, value): # FIXME from_fds
#        try: self.element.diffuse_color = value[0]/255, value[1]/255, value[2]/255
#        except: raise BFException(self, "Unknown RGB color value '{}'".format(value))

@subscribe
class MP_TRANSPARENCY(BFNoAutoUIMod, BFProp): # ui is statically added in the material panel
    label = "TRANSPARENCY"
    description = "Transparency"
    fds_label = "TRANSPARENCY"
    bpy_type = Material
    bpy_prop = None # Do not register
    bpy_idname = "alpha"

    def get_exported(self, context):
        # Export me only if transparency is set
        return self.element.alpha < 1.

@subscribe
class MP_THICKNESS_export(BFExportProp):
    bpy_idname = "bf_thickness_export"
    bpy_type = Material

@subscribe
class MP_THICKNESS(BFProp):
    label = "THICKNESS [m]"
    description = "Surface thickness for heat transfer calculation"
    fds_label = "THICKNESS"
    bf_prop_export = MP_THICKNESS_export
    bpy_type = Material
    bpy_idname = "bf_thickness"
    bpy_prop = FloatProperty
    bpy_default = .01
    bpy_other = {
        "step": 1.,
        "precision": 3,
        "min": .001,
    }
    # "unit": "LENGTH", # correction for scale_length needed before exporting!

@subscribe
class MP_HRRPUA(BFProp):
    label = "HRRPUA [kW/m²]"
    description = "Heat release rate per unit area"
    fds_label = "HRRPUA"
    bpy_type = Material
    bpy_idname = "bf_hrrpua"
    bpy_prop = FloatProperty
    bpy_default = 1000.
    bpy_other = {
        "step": 1000.,
        "precision": 3,
        "min": 0.,
    }

@subscribe
class MP_TAU_Q(BFProp):
    label = "TAU_Q [s]"
    description = "Ramp time for heat release rate"
    fds_label = "TAU_Q"
    bpy_type = Material
    bpy_idname = "bf_tau_q"
    bpy_prop = FloatProperty
    bpy_default = 100.
    bpy_other =  {
        "step": 10.,
        "precision": 1,
        "unit": "TIME",
    }

    def check(self, context):
        self.infos.append((
            self.element.bf_tau_q <= 0 and "HRR(t) has a t² ramp" or "HRR(t) has a tanh(t/τ) ramp",
            "material.set_tau_q"
        )) # info, operator

@subscribe
class MP_MATL_ID_export(BFExportProp):
    bpy_idname = "bf_matl_id_export"
    bpy_type = Material

@subscribe
class MP_MATL_ID(BFStringProp):
    label = "MATL_ID"
    description = "Reference to a MATL (Material) line for self properties"
    fds_label = "MATL_ID"
    bf_prop_export = MP_MATL_ID_export
    bpy_type = Material
    bpy_idname = "bf_matl_id"

@subscribe
class MP_IGNITION_TEMPERATURE_export(BFExportProp):
    bpy_idname = "bf_ignition_temperature_export"
    bpy_type = Material

@subscribe
class MP_IGNITION_TEMPERATURE(BFProp):
    label = "IGNITION_TEMPERATURE [°C]"
    description = "Ignition temperature"
    fds_label = "IGNITION_TEMPERATURE"
    bf_prop_export = MP_IGNITION_TEMPERATURE_export
    bpy_type = Material
    bpy_idname = "bf_ignition_temperature"
    bpy_prop = FloatProperty
    bpy_default = 300.
    bpy_other =  {
        "step": 100.,
        "precision": 1,
        "min": -273.,
    }

@subscribe
class MN_SURF(BFNamelist):
    label = "SURF"
    description = "Generic Boundary Condition"
    enum_id = 2000
    fds_label = "SURF"
    bpy_type = Material
    bf_prop_export = MP_export
    bf_props = MP_ID, MP_FYI, MP_RGB, MP_TRANSPARENCY, MP_MATL_ID, MP_THICKNESS, MP_free

@subscribe
class MN_SURF_burner(BFNamelist):
    label = "SURF"
    description = "Spec'd rate burner"
    enum_id = 2001
    fds_label = "SURF"
    bpy_type = Material
    bf_prop_export = MP_export
    bf_props = MP_ID, MP_FYI, MP_RGB, MP_TRANSPARENCY, MP_HRRPUA, MP_TAU_Q, MP_free

@subscribe
class MN_SURF_solid(BFNamelist):
    label = "SURF"
    description = "Spec'd rate burning solid"
    enum_id = 2002
    fds_label = "SURF"
    bpy_type = Material
    bf_prop_export = MP_export
    bf_props = MP_ID, MP_FYI, MP_RGB, MP_TRANSPARENCY, MP_HRRPUA, MP_TAU_Q, MP_MATL_ID, MP_IGNITION_TEMPERATURE, MP_THICKNESS, MP_free


### Object namelists and their specific properties

@subscribe
class OP_export(BFExportProp):
    bpy_type = Object
    bpy_default = True

@subscribe
class OP_show_transparent(BFNoAutoUIMod, BFNoAutoExportMod, BFProp): # Useful for bpy_props_copy operator
    label = "Show Object Transparency"
    description = "Show Object Transparency"
    bpy_type = Object
    bpy_prop = None # Do not register
    bpy_idname = "show_transparent"

@subscribe
class OP_draw_type(BFNoAutoUIMod, BFNoAutoExportMod, BFProp): # Useful for bpy_props_copy operator
    label = "Draw Type"
    description = "Draw type"
    bpy_type = Object
    bpy_prop = None # Do not register
    bpy_idname = "draw_type"

@subscribe
class OP_hide(BFNoAutoUIMod, BFNoAutoExportMod, BFProp): # Useful for bpy_props_copy operator
    label = "Hide"
    description = "Hide object"
    bpy_type = Object
    bpy_prop = None # Do not register
    bpy_idname = "hide"

@subscribe
class OP_hide_select(BFNoAutoUIMod, BFNoAutoExportMod, BFProp): # Useful for bpy_props_copy operator
    label = "Hide From Selection"
    description = "Hide from selection"
    bpy_type = Object
    bpy_prop = None # Do not register
    bpy_idname = "hide_select"

@subscribe
class OP_id_suffix(BFNoAutoUIMod, BFNoAutoExportMod, BFProp):
    label = "ID Suffix"
    description = "Append suffix to multiple ID values"
    fds_label = None
    bpy_type = Object
    bpy_idname = "bf_id_suffix"
    bpy_prop = EnumProperty
    bpy_default = "IDI"
    bpy_other = {
        "items": (
            ("IDI",   "Index", "Append index number to multiple ID values", 100),
            ("IDX",   "x",     "Append x coordinate to multiple ID values", 200),
            ("IDY",   "y",     "Append y coordinate to multiple ID values", 300),
            ("IDZ",   "z",     "Append z coordinate to multiple ID values", 400),
            ("IDXY",  "xy",    "Append x,y coordinates to multiple ID values", 500),
            ("IDXZ",  "xz",    "Append x,z coordinates to multiple ID values", 600),
            ("IDYZ",  "yz",    "Append y,z coordinates to multiple ID values", 700),
            ("IDXYZ", "xyz",   "Append x,y,z coordinates to multiple ID values", 800),
        ),
    }

@subscribe
class OP_ID(BFStringProp):
    label = "ID"
    description = "Object identificator"
    overwrite = False # Do not allow replacement
    fds_label = "ID"
    bf_props = OP_id_suffix, OP_show_transparent, OP_draw_type, OP_hide, OP_hide_select
    bpy_type = Object
    bpy_prop = None # Do not register
    bpy_idname = "name"

    def _draw_body(self, context, layout):
        row = layout.split(.8, align=True)
        row.template_ID(context.scene.objects, "active")
        row.prop(self.element, "bf_id_suffix", text="")

@subscribe
class OP_FYI(BFFYIProp):
    bpy_type = Object

@subscribe
class OP_free(BFFreeProp):
    bpy_type = Object

# OBST

@subscribe
class OP_SURF_ID(BFProp):
    label = "SURF_ID"
    description = "Reference to SURF"
    fds_label = "SURF_ID"
    bpy_type = Object
    bpy_idname = "active_material"
    bpy_prop = None # Do not register

    def get_exported(self, context):
        return self.element.active_material and self.element.active_material.bf_export

    def to_fds(self, context): # FIXME test
        if self.get_exported(context): return "SURF_ID='{}'".format(self.element.active_material.name)
        
#    def get_value(self):
#        if self.element.active_material: return self.element.active_material.name

    def from_fds(self, context, value): # FIXME test
        try: self.element.active_material = geometry.geom_utils.get_material(context, str(value))
        except: raise BFException(self, "Error in setting '{}' Blender material".format(value))

#    def set_value(self, context, value):
#        try: self.element.active_material = geometry.geom_utils.get_material(context, str(value))
#        except: raise BFException(self, "Error in setting '{}' Blender material".format(value))

@subscribe
class OP_OBST_THICKEN(BFBoolProp):
    label = "THICKEN"
    description = "Prevent FDS from allowing thin sheet obstructions"
    fds_label = "THICKEN"
    bpy_type = Object
    bpy_idname = "bf_obst_thicken"
    bpy_default = False

@subscribe
class ON_OBST(BFNamelist):
    label = "OBST"
    description = "Obstruction"
    enum_id = 1000
    fds_label = "OBST"
    bpy_type = Object
    bf_prop_export = OP_export
    bf_props = OP_ID, OP_id_suffix, OP_FYI, OP_SURF_ID, OP_XB_solid, OP_OBST_THICKEN, OP_free


# HOLE

@subscribe
class ON_HOLE(BFNamelist):
    label = "HOLE"
    description = "Obstruction Cutout"
    enum_id = 1009
    fds_label = "HOLE"
    bpy_type = Object
    bf_prop_export = OP_export
    bf_props = OP_ID, OP_FYI , OP_XB_solid, OP_free
    bf_appearance = {"draw_type": "WIRE"}


# VENT

@subscribe
class ON_VENT(BFNamelist):
    label = "VENT"
    description = "Boundary Condition Patch"
    enum_id = 1010
    fds_label = "VENT"
    bpy_type = Object
    bf_prop_export = OP_export
    bf_props = OP_ID, OP_FYI, OP_SURF_ID, OP_XB_faces, OP_XYZ, OP_PB, OP_free


# DEVC

@subscribe
class OP_DEVC_QUANTITY(BFStringProp):
    label = "QUANTITY"
    description = "Output quantity"
    fds_label = "QUANTITY"
    bpy_type = Object
    bpy_idname = "bf_quantity"

@subscribe
class OP_DEVC_SETPOINT_export(BFExportProp):
    bpy_idname = "bf_devc_setpoint_export"
    bpy_type = Object

@subscribe
class OP_DEVC_SETPOINT(BFProp):
    label = "SETPOINT [~]"
    description = "Value of the device at which its state changes"
    fds_label = "SETPOINT"
    bpy_type = Object
    bf_prop_export = OP_DEVC_SETPOINT_export
    bpy_idname = "bf_devc_setpoint"
    bpy_prop = FloatProperty
    bpy_default = 100.
    bpy_other =  {
        "step": 10.,
        "precision": 3,
    }

@subscribe
class OP_DEVC_INITIAL_STATE(BFBoolProp):
    label = "INITIAL_STATE"
    description = "Set device initial state to .TRUE."
    fds_label = "INITIAL_STATE"
    bpy_type = Object
    bpy_idname = "bf_devc_initial_state"
    bpy_default = False

@subscribe
class OP_DEVC_LATCH(BFBoolProp):
    label = "LATCH"
    description = "Device only changes state once"
    fds_label = "LATCH"
    bpy_type = Object
    bpy_idname = "bf_devc_latch"
    bpy_default = False

@subscribe
class OP_DEVC_PROP_ID(BFStringProp):
    label = "PROP_ID"
    description = "Reference to a PROP (Property) line for self properties"
    fds_label = "PROP_ID"
    bpy_type = Object
    bpy_idname = "bf_devc_prop_id"

@subscribe
class ON_DEVC(BFNamelist):
    label = "DEVC"
    description = "Device"
    enum_id = 1011
    fds_label = "DEVC"
    bpy_type = Object
    bf_prop_export = OP_export
    bf_props = OP_ID, OP_FYI, OP_DEVC_QUANTITY, OP_DEVC_SETPOINT, OP_DEVC_INITIAL_STATE, OP_DEVC_LATCH, OP_DEVC_PROP_ID, OP_XB, OP_XYZ, OP_free
    bf_appearance = {"draw_type": "WIRE"}


# SLCF

@subscribe
class OP_SLCF_VECTOR(BFBoolProp):
    label = "VECTOR"
    description = "Create animated vectors"
    fds_label = "VECTOR"
    bpy_type = Object
    bpy_idname = "bf_slcf_vector"
    bpy_default = False

@subscribe
class ON_SLCF(BFNamelist):
    label = "SLCF"
    description = "Slice File"
    enum_id = 1012
    fds_label = "SLCF"
    bpy_type = Object
    bf_prop_export = OP_export
    bf_props = OP_ID, OP_FYI, OP_DEVC_QUANTITY, OP_SLCF_VECTOR, OP_XB_faces, OP_PB, OP_free
    bf_appearance = {"draw_type": "WIRE"}


# PROF

@subscribe
class ON_PROF(BFNamelist):
    label = "PROF"
    description = "Wall Profile Output"
    enum_id = 1013
    fds_label = "PROF"
    bpy_type = Object
    bf_prop_export = OP_export
    bf_props = OP_ID, OP_FYI, OP_DEVC_QUANTITY, OP_XYZ, OP_free
    bf_appearance = {"draw_type": "WIRE"}


# MESH

@subscribe
class OP_MESH_IJK_export(BFExportProp):
    bpy_idname = "bf_mesh_ijk_export"
    bpy_type = Object

@subscribe
class OP_MESH_IJK(BFProp):
    label = "IJK"
    description = "Cell number in x, y, and z direction"
    fds_label = "IJK"
    bf_prop_export = OP_MESH_IJK_export
    bpy_type = Object
    bpy_idname = "bf_mesh_ijk"
    bpy_prop = IntVectorProperty
    bpy_default = (10,10,10)
    bpy_other =  {"size":3, "min":1}

    def check(self, context):
        # Init
        has_good_ijk, cell_sizes, cell_number, cell_aspect_ratio  = mesh.get_cell_infos(context, self.element)
        # Get and compare good IJK
        if not has_good_ijk:
            self.infos.append((
                "J and K not optimal for Poisson solver",
                "object.bf_correct_ijk"
            )) # info, operator
        # Info on cells
        self.infos.append((
            "{0} mesh cells of size {1[0]:.3f}x{1[1]:.3f}x{1[2]:.3f} m".format(cell_number, cell_sizes),
            "object.bf_set_cell_sizes"
        ))  # info, operator
        # Info on aspect ratio
        if cell_aspect_ratio > 2.:
            self.infos.append("Max cell aspect ratio is {:.1f}".format(cell_aspect_ratio))             

@subscribe
class ON_MESH(BFNamelist):
    label = "MESH"
    description = "Domain of simulation"
    enum_id = 1014
    fds_label = "MESH"
    bpy_type = Object
    bf_prop_export = OP_export
    bf_props = OP_ID, OP_FYI, OP_MESH_IJK, OP_XB_bbox, OP_free
    bf_appearance = {"draw_type": "WIRE"}


# INIT

@subscribe
class ON_INIT(BFNamelist):
    label = "INIT"
    description = "Initial condition"
    enum_id = 1015
    fds_label = "INIT"
    bpy_type = Object
    bf_prop_export = OP_export
    bf_props = OP_ID, OP_FYI, OP_XB_solid, OP_XYZ, OP_free
    bf_appearance = {"draw_type": "WIRE"}


# ZONE

@subscribe
class ON_ZONE(BFNamelist):
    label = "ZONE"
    description = "Pressure zone"
    enum_id = 1016
    fds_label = "ZONE"
    bpy_type = Object
    bf_prop_export = OP_export
    bf_props = OP_ID, OP_FYI, OP_XB_bbox, OP_free
    bf_appearance = {"draw_type": "WIRE"}


# free

@subscribe
class OP_free_namelist(BFProp):
    label = "Namelist"
    description = "Free namelist, eg <ABCD>"
    bpy_type = Object
    bpy_idname = "bf_free_namelist"
    bpy_prop = StringProperty
    bpy_default = "ABCD"
    bpy_other =  {"maxlen": 4}

    def check(self, context):
        value = self.element.bf_free_namelist
        # Matches "OBST"
        if not re.match("^[A-Z0-9_]{4}$", value):
            raise BFException(self, "Malformed free namelist")

    def to_fds(self, context):
        self.check(context)
        return self.element.bf_free_namelist

@subscribe
class ON_free(BFNamelist):
    label = "Free Namelist"
    description = "Free Namelist"
    enum_id = 1007
    fds_label = None
    bpy_type = Object
    bf_prop_export = OP_export
    bf_props = OP_free_namelist, OP_ID, OP_FYI, OP_SURF_ID, OP_XB, OP_XYZ, OP_PB, OP_free
    

### Update OP_namelist_cls (menu for Object namelist selection) with all defined namelists
items = [bf_namelist.get_enum_item() for bf_namelist in BFNamelist.all if bf_namelist.bpy_type == Object]
items.sort(key=lambda k:k[1])
OP_namelist_cls.bpy_other["items"] = items

### Update MP_namelist_cls (menu for Material namelist selection) with all defined namelists
items = [bf_namelist.get_enum_item() for bf_namelist in BFNamelist.all if bf_namelist.bpy_type == Material]
items.sort(key=lambda k:k[1])
MP_namelist_cls.bpy_other["items"] = items

### DEBUG

if DEBUG:
    print("\nBFNamelist.all:\n",BFNamelist.all)
    print("\nBFProp.all:\n",BFProp.all)
    print()

