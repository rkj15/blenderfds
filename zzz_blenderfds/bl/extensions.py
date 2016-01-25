"""BlenderFDS, extended Blender types"""

import bpy, time
from bpy.types import Object, Material, Scene

from ..types import BFNamelist
from ..exceptions import BFException
from .. import geometry
from .. import fds
from .. import config

DEBUG = False

### Extend bpy.type.Object

class BFObject():
    """Extend Blender Object bpy.type"""

    def __str__(self):
        return "Object {}".format(self.name)

    @property
    def bf_namelist(self) -> "BFNamelist instance": # Only one namelist per object
        """Returns an instance of the linked Object namelist class."""
        if self.type != "MESH": return None
        ON_cls = BFNamelist.all.get(self.bf_namelist_cls) # get class from name
        if ON_cls: return ON_cls(element=self) # create instance from class

    def set_default_appearance(self, context):
        """Set default object appearance."""
        # Set draw_type
        draw_type = self.bf_namelist.bf_other.get("draw_type")
        if draw_type: self.draw_type = draw_type
        # Set hide_select
        hide_select = self.bf_namelist.bf_other.get("hide_select")
        if hide_select: self.hide_select = hide_select
        # Set show_transparent
        self.show_transparent = True

    def _myself_to_fds(self, context) -> "list": # FIXME test
        """Export myself in FDS notation."""
        bodies = list()
        if self.bf_export:
            if self.type == "MESH":
                bf_namelist = self.bf_namelist
                if bf_namelist:
                    body = bf_namelist.to_fds(context)
                    if body: bodies.append(body)  # could be None
            elif self.type == "EMPTY":
                bodies.append("! -- {}: {}\n".format(self.name, self.bf_fyi))
        return bodies

    def _children_to_fds(self, context) -> "list": # FIXME test
        """Export children in FDS notation."""
        # Init
        children_obs = [ob for ob in context.scene.objects if ob.parent == self]
        children_obs.sort(key=lambda k:k.name) # Order by element name
        children_obs.sort(key=lambda k:k.bf_namelist_cls!=("ON_MESH")) # Order MESHes first (False then True)
        # Children to_fds
        bodies = list()
        for ob in children_obs:
            body = ob.to_fds(context, with_children=True)
            if body: bodies.append(body)  # could be None
        if bodies: bodies.append("\n")
        # Return
        return bodies
   
    def to_fds(self, context, with_children=False) -> "str or None":  # FIXME test
        """Export myself and children in FDS notation."""
        bodies = list()
        bodies.extend(self._myself_to_fds(context))
        if with_children: bodies.extend(self._children_to_fds(context))
        return "".join(bodies)
        
# Add methods to original Blender type

Object.__str__ = BFObject.__str__
Object.bf_namelist = BFObject.bf_namelist
Object.set_default_appearance = BFObject.set_default_appearance
Object._myself_to_fds = BFObject._myself_to_fds
Object._children_to_fds = BFObject._children_to_fds
Object.to_fds = BFObject.to_fds

### Extend bpy.type.Material

class BFMaterial():
    """Extend Blender Material bpy.type"""

    def __str__(self):
        return "Material {}".format(self.name)

    @property
    def bf_namelist(self) -> "BFNamelist instance": # Only one namelist per material
        """Returns an instance of the linked Material namelist class"""
        MN_cls = BFNamelist.all.get(self.bf_namelist_cls) # get class from name
        if MN_cls: return MN_cls(element=self) # create instance from class

    def set_default_appearance(self, context):
        """Set default material appearance."""
        self.use_fake_user = True

    def to_fds(self, context) -> "str or None":
        """Export myself in FDS notation."""
        if self.bf_export and (self.name not in fds.surf.predefined):
            bf_namelist = self.bf_namelist
            if bf_namelist: return bf_namelist.to_fds(context)
        
# Add methods to original Blender type

Material.__str__ = BFMaterial.__str__
Material.bf_namelist = BFMaterial.bf_namelist
Material.set_default_appearance = BFMaterial.set_default_appearance
Material.to_fds = BFMaterial.to_fds

### Extend bpy.type.Scene

class BFScene():
    """Extend Blender Material bpy.type"""

    def __str__(self):
        return "Scene {}".format(self.name)

    @property
    def bf_namelists(self) -> "List of BFNamelist instances":  # Many namelists per scene
        """Returns a list of instances of the linked Scene namelist classes"""
        bf_namelists = [bf_namelist(element=self) for bf_namelist in BFNamelist.all if bf_namelist.bpy_type == Scene]
        bf_namelists.sort(key=lambda k:k.enum_id) # Order Scene namelists by enum_id
        return bf_namelists

    def set_default_appearance(self, context):
        self.unit_settings.system = 'METRIC'
        self.render.engine = 'CYCLES'  # for transparency visualisation

    # Export

    def _myself_to_fds(self, context) -> "list": # FIXME test
        """Export myself in FDS notation."""
        bodies = list()
        for bf_namelist in self.bf_namelists:
            body = bf_namelist.to_fds(context)
            if body: bodies.append(body)  # Could be None
        if bodies: bodies.append("\n")
        return bodies

    def _children_to_fds(self, context) -> "list": # FIXME test
        """Export children in FDS notation."""
        # Init
        bodies = list()
        # Materials
        bodies.append("! --- Boundary conditions (from Blender Materials)\n\n")
        mas = [ma for ma in bpy.data.materials]
        mas.sort(key=lambda k:k.name) # Alphabetic order by element name
        for ma in mas:
            body = ma.to_fds(context)
            if body: bodies.append(body)
        bodies.append("\n")
        # Objects
        bodies.append("! --- Geometric entities (from Blender Objects)\n\n")
        bodies.extend(Object._children_to_fds(self=None, context=context)) # Call objects without a parent
        bodies.append("\n")
        # Return
        return bodies

    def _header_to_fds(self, context) -> "tuple": # FIXME test
        """Export header in FDS notation."""
        return (
            "! Generated by BlenderFDS {} on Blender {}\n".format(
                "{0[0]}.{0[1]}.{0[2]}".format(config.supported_file_version),
                bpy.app.version_string,
            ),
            "! Case: {} (from Blender Scene)\n".format(self.name),
            "! Description: {}\n".format(self.bf_head_title),
            "! Date: {}\n".format(time.strftime("%a, %d %b %Y, %H:%M:%S", time.localtime())),
            "! File: {}\n\n".format(bpy.data.filepath),
        )

    def _free_text_to_fds(self, context) -> "list": # FIXME test
        """Export HEAD free text in FDS notation."""
        bodies = list()
        if self.bf_head_free_text: # FIXME no error management
            bodies.append("! --- Free text: '{}'\n\n".format(self.bf_head_free_text))
            bodies.append(bpy.data.texts[self.bf_head_free_text].as_string())
            if bodies[-1][-1:] == "\n": bodies.append("\n")
            else: bodies.append("\n\n")
        return bodies

    def to_fds(self, context, with_children=False) -> "str or None":   # FIXME test
        """Export myself and children (full FDS case) in FDS notation."""
        # Init
        t0 = time.time()
        bodies = list()
        # Header, Scene, free_text
        if with_children: bodies.extend(self._header_to_fds(context))
        bodies.extend(self._myself_to_fds(context))
        bodies.extend(self._free_text_to_fds(context))
        # Materials, objects, TAIL
        if with_children:
            bodies.extend(self._children_to_fds(context))
            bodies.append("&TAIL /\n! Generated in {0:.0f} s.".format((time.time()-t0)))
        # Return
        return "".join(bodies)

    def to_ge1(self, context) -> "str or None":
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
        bpy_type = bf_namelist_cls.bpy_type
        if bpy_type == bpy.types.Scene:
            element = self # Import into self
        elif bpy_type == bpy.types.Object:
            element = geometry.geom_utils.get_new_object(context, self, name="New {}".format(fds_label)) # New Object
            element.bf_namelist_cls = bf_namelist_cls.__name__ # Set link to namelist
        elif bpy_type == bpy.types.Material:
            element = geometry.geom_utils.get_new_material(context, name="New {}".format(fds_label)) # New Material
            element.bf_namelist_cls = "MN_SURF" # Set link to default namelist
        else:
            raise ValueError("BFDS: BFScene.from_fds: Unrecognized namelist type!")
        element.set_default_appearance(context)
        return element

    def _save_imported_unmanaged_tokens(self, context, free_texts) -> "None":
        """Save unmanaged tokens to free text."""
        # Get or create free text file, then show
        bf_head_free_text = fds.head.set_free_text_file(context, self)
        # Get existing contents
        old_free_texts = bpy.data.texts[bf_head_free_text].as_string()
        if old_free_texts: free_texts.extend(("\n! --- Existing free texts\n",old_free_texts))
        # Write merged contents
        bpy.data.texts[bf_head_free_text].from_string("\n".join(free_texts))

    def from_fds(self, context, value):
        """Import a text in FDS notation into self. On error raise BFException.
        Value is any text in good FDS notation.
        """
        # Tokenize value and manage exception
        try: tokens = fds.to_py.tokenize(value)
        except Exception as err:  # TODO improve!
            raise BFException(self, "Unrecognized FDS syntax, cannot import.")
        # Treat tokens
        free_texts = list()
        errors = list()
        for token in tokens:
            # Init
            fds_original, fds_label, fds_value = token
            # Search managed FDS namelist, and import token
            bf_namelist_cls = self._get_imported_bf_namelist_cls(context, fds_label, fds_value)
            if bf_namelist_cls:
                # This FDS namelists is managed: get element, instanciate and import BFNamelist
                element = self._get_imported_element(context, bf_namelist_cls, fds_label, fds_value)
                try: bf_namelist_cls(element).from_fds(context, fds_value)
                except BFException as err:
                    errors.append(err)
                    free_texts.extend(err.free_texts) # Record in free_texts
            else:
                # This FDS namelists is not managed
                free_texts.append(fds_original)
        # Save free_texts, even if empty (remeber, bf_head_free_text is not set to default)
        self._save_imported_unmanaged_tokens(context, free_texts)
        # Return
        if errors: raise BFException(self, "Errors reported, see details in HEAD free text file.", errors)

# Add methods to original Blender type

Scene.__str__ = BFScene.__str__
Scene.bf_namelists = BFScene.bf_namelists
Scene.set_default_appearance = BFScene.set_default_appearance

Scene._myself_to_fds = BFScene._myself_to_fds
Scene._header_to_fds = BFScene._header_to_fds
Scene._free_text_to_fds = BFScene._free_text_to_fds
Scene._children_to_fds = BFScene._children_to_fds
Scene.to_fds = BFScene.to_fds
Scene.to_ge1 = BFScene.to_ge1

Scene._get_imported_bf_namelist_cls = BFScene._get_imported_bf_namelist_cls
Scene._get_imported_element = BFScene._get_imported_element
Scene._save_imported_unmanaged_tokens = BFScene._save_imported_unmanaged_tokens
Scene.from_fds = BFScene.from_fds

