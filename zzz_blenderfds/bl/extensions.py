"""BlenderFDS, extended Blender types"""

import bpy, time
from bpy.types import Object, Material, Scene

from ..types import BFNamelist
from ..exceptions import BFException
from .. import geometry
from .. import fds

from .. import config
from .operators import open_text_in_editor

DEBUG = False

### Extend bpy.type.Object

class BFObject():
    """Extend Blender Object bpy.type"""

    def _get_bf_namelist(self):
        """Returns an instance of the linked Object namelist class."""
        if self.type != "MESH": return None
        ON_cls = BFNamelist.all.get(self.bf_namelist_cls) # get class from name
        if ON_cls: return ON_cls(element=self) # create instance from class

    bf_namelist = property(_get_bf_namelist) # Only one namelist per object

    def set_default_appearance(self, context):
        """Set default object appearance."""
        bf_appearance = self.bf_namelist.bf_appearance
        self.show_transparent = True
        if bf_appearance:
            if "draw_type" in bf_appearance: self.draw_type = bf_appearance["draw_type"]
            if "hide" in bf_appearance: self.hide = bf_appearance["hide"]
            if "hide_select" in bf_appearance: self.hide_select = bf_appearance["hide_select"]
   
    def to_fds(self, context) -> "str or None":
        """Export me in FDS notation."""
        # Init
        w = context.window_manager.windows[0]
        w.cursor_modal_set("WAIT")
        bodies = list()

        # Export
        try:
            # Choose and call myself
            if self.type == "MESH":
                bf_namelist = self.bf_namelist
                if bf_namelist:
                    bodies.append(bf_namelist.to_fds(context) or str())  # could be None        
            elif self.type == "EMPTY":
                bodies.append("! -- {}: {}\n".format(self.name, self.bf_fyi))
            else: raise Exception("BFDS: Impossible to export '{}'".format(self.type))
            # Call children
            for ob in context.scene.objects:
                if ob.parent == self: bodies.append(ob.to_fds(context))
        except BFException as err: raise BFException(self, *err.labels)

        # Return
        w.cursor_modal_restore()
        return "".join(bodies)
        
# Add methods to original Blender type

Object.bf_namelist = BFObject.bf_namelist
Object.set_default_appearance = BFObject.set_default_appearance
Object.to_fds = BFObject.to_fds

### Extend bpy.type.Material

class BFMaterial():
    """Extend Blender Material bpy.type"""

    def _get_bf_namelist(self):
        """Returns an instance of the linked Material namelist class"""
        MN_cls = BFNamelist.all.get(self.bf_namelist_cls) # get class from name
        if MN_cls: return MN_cls(element=self) # create instance from class

    bf_namelist = property(_get_bf_namelist) # Only one namelist per material

    def set_default_appearance(self, context):
        self.use_fake_user = True

    def to_fds(self, context) -> "str or None":
        """Export me in FDS notation."""
        # Init
        w = context.window_manager.windows[0]
        w.cursor_modal_set("WAIT")
        body = None

        # Export
        try:
            # Myself
            bf_namelist = self.bf_namelist
            if bf_namelist: body = bf_namelist.to_fds(context) or str()  # could be None
        except BFException as err: raise BFException(self, *err.labels)

        # Return
        w.cursor_modal_restore()
        return body

Material.bf_namelist = BFMaterial.bf_namelist
Material.set_default_appearance = BFMaterial.set_default_appearance
Material.to_fds = BFMaterial.to_fds

### Extend bpy.type.Scene

class BFScene():
    """Extend Blender Material bpy.type"""

    def _get_bf_namelists(self):
        """Returns a list of instances of the linked Scene namelist classes"""
        bf_namelists = [bf_namelist(element=self) for bf_namelist in BFNamelist.all if bf_namelist.bpy_type == Scene]
        bf_namelists.sort(key=lambda k:k.enum_id) # Order Scene namelists by enum_id
        return bf_namelists

    bf_namelists = property(_get_bf_namelists) # Many namelists per scene

    def set_default_appearance(self, context):
        pass

    # Export

    def to_fds(self, context) -> "str or None":
        """Export me in FDS notation."""
        # Init
        w = context.window_manager.windows[0]
        w.cursor_modal_set("WAIT")
        bodies = list()

        # Export
        try:
            # Myself
            for bf_namelist in self.bf_namelists:
                bodies.append(bf_namelist.to_fds(context) or str())
        except BFException as err: raise BFException(self, *err.labels)

        # Return
        w.cursor_modal_restore()
        return "".join(bodies)

    def to_fds_case(self, context) -> "str or None":
        """Export full case in FDS notation."""
        # Init
        t0 = time.time()
        w = context.window_manager.windows[0]
        w.cursor_modal_set("WAIT")
        bodies = list()

        # Header
        bodies.append("! Generated by BlenderFDS {} on Blender {}\n! Case: {}\n! Description: {}\n! Date: {}\n! File: {}\n\n".format(
            "{0[0]}.{0[1]}.{0[2]}".format(config.supported_file_version), bpy.app.version_string,
            self.name,
            self.bf_head_title,
            time.strftime("%a, %d %b %Y, %H:%M:%S", time.localtime()),
            bpy.data.filepath,
        ))

        # Scene
        bodies.append("! --- Configuration\n\n")
        bodies.append(self.to_fds(context))
        bodies.append("\n")

        # Free text
        bodies.append("! --- Free text: '{}'\n\n".format(self.bf_head_free_text))
        if self.bf_head_free_text:
            bodies.append(bpy.data.texts[self.bf_head_free_text].as_string())
        if bodies[-1][-1:] == "\n": bodies.append("\n")
        else: bodies.append("\n\n")

        # Export materials
        bodies.append("! --- Boundary conditions\n\n")
        mas = [ma for ma in bpy.data.materials 
            if ma.bf_export and (ma.name not in fds.surf.predefined)]
        mas.sort(key=lambda k:k.name) # Alphabetic order by element name
        for ma in mas:
            bodies.append(ma.to_fds(context))
        bodies.append("\n")

        # Export objects
        bodies.append("! --- Geometric entities\n\n")
        obs = [ob for ob in context.scene.objects \
            if ob.type in ("MESH", "EMPTY",) and ob.parent == None and ob.bf_export]
        obs.sort(key=lambda k:k.name) # Order by element name
        obs.sort(key=lambda k:k.bf_namelist_cls!=("ON_MESH")) # Order MESHes first (False then True)
        for ob in obs:
            bodies.append(ob.to_fds(context))
        bodies.append("\n")

        # Set tail
        bodies.append("&TAIL /\n! Generated in {0:.0f} s.".format((time.time()-t0)))

        # Return
        w.cursor_modal_restore()
        return "".join(bodies)

    def to_ge1(self, context):
        """Export my geometry in FDS GE1 notation."""
        return geometry.to_ge1.scene_to_ge1(context, self)

    # Import

    def _get_imported_bf_namelist_cls(self, context, fds_label, fds_value) -> "BFNamelist or None":
        """Try to get managed BFNamelist from fds_label."""
        bf_namelist_cls = BFNamelist.all.get_by_fds_label(fds_label)
        if not bf_namelist_cls:
            if set(("XB", "XYZ", "PBX", "PBY", "PBZ")) & set(prop[1] for prop in fds_value):
                # An unmanaged geometric namelist
                bf_namelist_cls = BFNamelist.all["ON_free"] # Link to free namelist
        return bf_namelist_cls

    def _get_imported_element(self, context, bf_namelist_cls, fds_label, fds_value) -> "Element":
        """Get element."""
        # Init
        bpy_type = bf_namelist_cls.bpy_type
        imported_element_name = {prop[1]: prop[2] for prop in fds_value}.get("ID", None)
        # Is Scene
        if bpy_type == bpy.types.Scene: element = self
        # Is Object
        elif bpy_type == bpy.types.Object:
            element = geometry.utils.get_object_by_name(context, name=imported_element_name)
            if not element: element = geometry.utils.get_new_object(context, name="New {}".format(fds_label))
            element.bf_namelist_cls = bf_namelist_cls.__name__ # Set link to namelist
        # Is Material
        elif bpy_type == bpy.types.Material:
            element = geometry.utils.get_material_by_name(context, name=imported_element_name)
            if not element: element = geometry.utils.get_new_material(context, name="New {}".format(fds_label))
        # Is Unknown
        else: raise ValueError("BFDS: BFScene.from_fds: Unrecognized namelist type!")
        # Appearance
        element.set_default_appearance(context)
        return element

    def _save_imported_unmanaged_tokens(self, context, free_texts) -> "None":
        """Save unmanaged tokens to free text."""
        # If not existing, create
        if not self.bf_head_free_text:
            self.bf_head_free_text = "HEAD free text ({})".format(self.name)    
            bpy.data.texts.new(self.bf_head_free_text)
        bf_head_free_text = self.bf_head_free_text
        # Prepare
        free_texts.insert(0,"! Imported\n")
        if bpy.data.texts[bf_head_free_text]:
            free_texts.append("\n! Previous\n")
            free_texts.append(bpy.data.texts[bf_head_free_text].as_string())
        # Write and show
        bpy.data.texts[bf_head_free_text].from_string("\n".join(free_texts))
        open_text_in_editor(context, bf_head_free_text)

    def from_fds(self, context, value, snippet=False):
        """Import a text in FDS notation into self. On error raise BFException.
        Value is any text in good FDS notation.
        """
        # Init
        w = context.window_manager.windows[0]
        w.cursor_modal_set("WAIT")

        # Tokenize value and manage exception
        try: tokens = fds.to_py.tokenize(value)
        except Exception as err:
            w.cursor_modal_restore()
            raise BFException(self, "Unrecognized FDS syntax, cannot import.")

        # Treat tokens
        free_texts = list()
        is_error_reported = False
        for token in tokens:
            # Init
            fds_original, fds_label, fds_value = token
            bf_namelist_cls = self._get_imported_bf_namelist_cls(context, fds_label, fds_value)
            # This FDS namelist is not managed
            if not bf_namelist_cls:
                free_texts.append(fds_original)
                continue
            # If snippet, check if overwrite of namelist is allowed (eg. SN_HEAD...)
            if snippet and not bf_namelist_cls.overwrite: continue
            # Get or create element, then instanciate BFNamelist
            element = self._get_imported_element(context, bf_namelist_cls, fds_label, fds_value)
            bf_namelist = bf_namelist_cls(element)
            # Import token
            try: bf_namelist.from_fds(context, fds_value, snippet)
            except BFException as err:
                is_error_reported = True
                free_texts.extend(err.fds_labels)
        # Save unmanaged tokens to free text
        if free_texts: self._save_imported_unmanaged_tokens(context, free_texts)
        # Return
        w.cursor_modal_restore()
        if is_error_reported: raise BFException(self, "Errors reported, see details in HEAD free text file.")

Scene.bf_namelists = BFScene.bf_namelists
Scene.set_default_appearance = BFScene.set_default_appearance
Scene.to_fds = BFScene.to_fds
Scene.to_fds_case = BFScene.to_fds_case
Scene.to_ge1 = BFScene.to_ge1

Scene._get_imported_bf_namelist_cls = BFScene._get_imported_bf_namelist_cls
Scene._get_imported_element = BFScene._get_imported_element
Scene._save_imported_unmanaged_tokens = BFScene._save_imported_unmanaged_tokens
Scene.from_fds = BFScene.from_fds

