"""BlenderFDS, types"""

from bpy.props import *

from .exceptions import BFException
from .utils import isiterable

from . import config
from .config import DEBUG


# Collections

def subscribe(cls):
    """Subscribe class to related collections."""
    # Subscribe to class collection 'self.all'
    cls.all.add(cls)
    # Subscribe to other useful dicts: self.all_by_fds_label, self.all_by_cls_name
    if cls.fds_label: cls.all_by_fds_label[cls.fds_label] = cls 
    cls.all_by_cls_name[cls.__name__] = cls
    # Subscribe to other useful dicts, but init specific dict for each new class
    # Build my cls.all_bf_props
    cls.all_bf_props = set()
    if cls.bf_prop_export: cls.all_bf_props.add(cls.bf_prop_export)
    if cls.bf_prop_free: cls.all_bf_props.add(cls.bf_prop_free)
    for bf_prop in cls.bf_props:
        cls.all_bf_props.add(bf_prop)
        cls.all_bf_props |= bf_prop.all_bf_props
    # Build my cls.all_bf_props_by_fds_label
    cls.all_bf_props_by_fds_label = dict()
    for bf_prop in cls.all_bf_props:
        if bf_prop.fds_label: cls.all_bf_props_by_fds_label[bf_prop.fds_label] = bf_prop
    # Build my cls.all_bf_props_by_cls_name
    cls.all_bf_props_by_cls_name = dict()
    for bf_prop in cls.all_bf_props:
        cls.all_bf_props_by_cls_name[bf_prop.__name__] = bf_prop
    # Return
    return cls

# BFProp and BFNamelist are used for short lived instances.
# When calling a Blender Element bf_namelist or bf_namelists method,
# the BFNamelist and all related BFProps are instantiated, then quickily forgotten
# This mechanism is used to draw panels and to export to FDS.

@subscribe # This is used to subscribe the class to the collections
class _BFCommon():
    """Common part of BFProp and BFNamelist"""
       
    all = set()                 # Collection of all classes (see subscribe)
    all_by_fds_label = dict()   # ... by fds label (see subscribe)
    all_by_cls_name = dict()    # ... by cls name (see subscribe)
    
    all_bf_props = set()        # Collection of all my managed bf_props, included descendants (reinit for every new class) (see subscribe)
    all_bf_props_by_fds_label = dict()  # ... by fds_label (see subscribe)
    all_bf_props_by_cls_name = dict()   # ... by cls name (see subscribe)

    label = "No Label"      # Object label
    description = "No desc" # Object description
    overwrite = True        # Allowed overwrite on copy/import operations
    enum_id = 0             # Unique integer id for EnumProperty
    fds_label = None        # FDS label as "OBST", "ID", ...

    bf_sys = False          # This property needs early registration
    
    bf_prop_export = None   # Class of type BFExportProp, used for setting if exported
    bf_props = []           # List of related BFProp
    bf_prop_free = None     # Class of type BFFreeProp, used for free text parameters

    bf_appearance = {}      # Optional BlenderFDS parameters related to element appearance in 3DView    
    bf_other = {}           # Other optional BlenderFDS parameters,
                            # eg: {'prop1': value1, ...}

    bpy_type = None         # type in bpy.types for Blender property, eg. Object
    bpy_idname = None       # idname of related bpy.types Blender property, eg. "bf_id"
    bpy_prop = None         # prop in bpy.props of Blender property, eg. StringProperty
    bpy_default = None      # default value of Blender property, eg True
    bpy_other = {}          # Other optional Blender property parameters,
                            # eg. {"min": 3., ...}

    def __init__(self, element):
        # The instance contains the reference to element
        self.element = element
        # Replace linked BFProp classes with their instances
        if self.bf_prop_export: self.bf_prop_export = self.bf_prop_export(element)
        if self.bf_props: self.bf_props = [bf_prop(element) for bf_prop in self.bf_props]
        if self.bf_prop_free: self.bf_prop_free = self.bf_prop_free(element)
        # Init exporting variables
        self.infos = list()
        # Instance constants
        self.bf_prop_by_fds_label = {
            bf_prop.fds_label: bf_prop for bf_prop in self.bf_props if bf_prop.fds_label
        }
        self.bf_prop_by_cls = {
            bf_prop.__class__: bf_prop for bf_prop in self.bf_props
        }

    def __repr__(self):
        return "{__class__.__name__!s}(element={element!r})".format(
            __class__ = self.__class__,
            **self.__dict__
        )

    def __str__(self):
        return "{}:{}".format(self.element.name, self.label)

    # Register/Unregister

    @classmethod
    def register(cls):
        """Register all related Blender properties."""
        print("BFDS: BFProp.register:", cls.__name__)
        if not cls.bpy_type: raise Exception("No bpy_type in class '{}'".format(cls.__name__))
        # Register my own Blender property, if needed
        if cls.bpy_prop and cls.bpy_idname and not hasattr(cls.bpy_type, cls.bpy_idname):
            if DEBUG:
                print("BFDS:  ", '{}.{} = {}(name="{}")'.format(
                    cls.bpy_type.__name__,
                    cls.bpy_idname,
                    cls.bpy_prop.__name__,
                    cls.label
                ))
            setattr(
                cls.bpy_type,
                cls.bpy_idname,
                cls.bpy_prop(name=cls.label, description=cls.description, default=cls.bpy_default, **cls.bpy_other)
            )
        # Register bf_prop_export, all bf_props, and bf_prop_free
        if cls.bf_prop_export: cls.bf_prop_export.register()
        for bf_prop in cls.bf_props: bf_prop.register()
        if cls.bf_prop_free: cls.bf_prop_free.register()

    @classmethod
    def unregister(cls):
        """Unregister all related Blender properties."""
        print("BFDS: BFProp.unregister:", cls.__name__) # TODO unregister

    # UI

    def _draw_messages(self, context, layout) -> "None":
        """Draw messages."""
        # Check self and trap errors
        try: self.check(context) 
        except BFException as err: err.draw(context, layout)
        # Draw infos
        for info in self.infos:
            if isiterable(info):
                row = layout.split(.7)
                row.label(icon="INFO", text=info[0])
                row.operator(info[1])
            else:
                layout.label(icon="INFO", text=info)

    def _draw_extra(self, context, layout) -> "None":
        """Draw extra widgets"""
        pass

    # Check

    def check(self, context):
        """Check self, append str infos to self.infos, on error raise BFException."""
        pass

    # Export

    def get_value(self) -> "any or None":
        """Get my Blender property value for element."""
        # None is not accepted as attribute name, replaced with str()
        return getattr(self.element, self.bpy_idname or str(), None)

    def set_value(self, context, value) -> "any or None":
        """Set my Blender property to value for element."""
        if self.bpy_idname: setattr(self.element, self.bpy_idname, value)

    def set_default_value(self, context) -> "any or None":
        """Set my Blender property to default value for element."""
        default = self.bpy_default
        if default is not None: self.set_value(context, default)

    def get_exported(self, context) -> "bool":
        """Return True if self is exported to FDS."""
        if self.bf_prop_export: return self.bf_prop_export.get_value()
        return True

    def set_exported(self, context, value) -> "any or None":
        """Set to value if self is exported to FDS."""
        if self.bf_prop_export: self.bf_prop_export.set_value(context, value)

    def set_default(self, context) -> "any or None":
        """Set me to default for element."""
        self.set_default_value(context)
        for bf_prop in self.all_bf_props:
            bf_prop = bf_prop(self.element) # Instanciate!
            bf_prop.set_default_value(context)


class BFProp(_BFCommon):
    """BlenderFDS property, interface between a Blender property and an FDS parameter."""
       
    all = set() # Re-init to obtain specific collection
    all_by_fds_label = dict()
    all_by_cls_name = dict()

    all_bf_props = set()
    all_bf_props_by_fds_label = dict()
    all_bf_props_by_cls_name = dict()

    # UI

    def _transform_layout(self, context, layout) -> "layout":
        """If self has a bf_prop_export, prepare double-column Blender panel layout."""
        layout = layout.row()
        if self.bf_prop_export:
            # Set two distinct colums: layout_export and layout_ui
            layout_export, layout = layout.column(), layout.column()
            layout_export.prop(self.element, self.bf_prop_export.bpy_idname, text="")
        else:
            layout = layout.column()
        layout.active = bool(self.get_exported(context)) # if not exported, layout is inactive. Protect it from None
        return layout

    def _draw_body(self, context, layout) -> "None":
        """Draw bpy_prop"""
        if not self.bpy_idname: return
        row = layout.row()
        row.prop(self.element, self.bpy_idname, text=self.label)

    def draw(self, context, layout) -> "None":
        """Draw my part of Blender panel."""
        layout = self._transform_layout(context, layout)
        self._draw_body(context, layout)
        self._draw_extra(context, layout)
        self._draw_messages(context, layout)

    # Export

    def format(self, context, value):
        """Format to FDS notation."""
        # Expected output:
        #   ID='example' or PI=3.14 or COLOR=3,4,5
        if value is None: return None
        # If value is not an iterable, then put it in a tuple
        if not isiterable(value): values = tuple((value,)) 
        else: values = value
        # Check first element of the iterable and choose formatting
        if   isinstance(values[0], bool):
            value = ",".join(value and ".TRUE." or ".FALSE." for value in values)
        elif isinstance(values[0], int):
            value = ",".join(str(value) for value in values)
        elif isinstance(values[0], float):
            value = ",".join("{:.{}f}".format(value, self.bpy_other.get("precision",3)) for value in values)
        elif isinstance(values[0], str) and value: # value is not ""
            value = ",".join("'{}'".format(value) for value in values)
        else:
            return None
        # Return
        if self.fds_label: return "=".join((self.fds_label, value))
        return str(value)

    def to_fds(self, context):
        """Get my exported FDS string, on error raise BFException."""
        if not self.get_exported(context): return None
        self.check(context)
        value = self.get_value()
        return self.format(context, value)

    # Import

    def from_fds(self, context, value):
        """Set my value from value in FDS notation, on error raise BFException.
        Value is any type of data compatible with bpy_prop
        Eg: "String", (0.2,3.4,1.2), ...
        """
        self.set_exported(context, True)
        self.set_value(context, value)


class BFNamelist(_BFCommon):
    """BlenderFDS namelist, interface between a Blender object and an FDS namelist."""
       
    all = set() # Re-init to obtain specific collection
    all_by_fds_label = dict()
    all_by_cls_name = dict()

    all_bf_props = set()
    all_bf_props_by_fds_label = dict()
    all_bf_props_by_cls_name = dict()    

    bf_appearance = {"draw_type": "SOLID"}
    
    # UI

    @classmethod
    def get_enum_item(cls) -> "List":
        """Get item for EnumProperty items."""
        return (
            cls.__name__,
            "{} ({})".format(cls.label, cls.description),
            cls.description,
            cls.enum_id
        )

    def draw_header(self, context, layout):
        """Draw Blender panel header."""
        if self.bf_prop_export: layout.prop(self.element, self.bf_prop_export.bpy_idname, text="")
        if self.description: return "BlenderFDS {} ({})".format(self.label, self.description)
        return "BlenderFDS {}".format(self.label)

    def _transform_layout(self, context, layout) -> "layout":
        """If self has a bf_prop_export, prepare Blender panel layout."""
        layout.active = self.get_exported(context)
        return layout

    def _draw_bf_props(self, context, layout):
        """Draw bf_props"""
        for bf_prop in self.bf_props or tuple(): bf_prop.draw(context, layout)

    def draw(self, context, layout) -> "None":
        """Draw my part of Blender panel."""
        layout = self._transform_layout(context, layout)
        self._draw_messages(context, layout)
        self._draw_bf_props(context, layout)
        if self.bf_prop_free: self.bf_prop_free.draw(context, layout)
        self._draw_extra(context, layout)

    # Export

    def format(self, context, params):
        """Format to FDS notation."""
        # Expected output:
        # ! name: info message 1
        # ! name: info message 2
        # &OBST ID='example' XB=... /\n
        # &OBST ID='example' XB=... /\n

        # Set separator
        separator = config.namelist_separator
        # Set fds_label, if empty use first param (OP_free_namelist)
        fds_label = "".join(("&", self.fds_label or params.pop(0), " "))
        # Set info
        infos = [isiterable(info) and info[0] or info for info in self.infos]
        info = "".join(("! {}\n".format(info) for info in infos))
        # Extract the first and only multiparams from params
        multiparams = None
        for param in params:
            if isiterable(param):
                multiparams = param
                params.remove(param)
                # ... then remove ordinary single ID
                for param in params:
                    if param[:3] == "ID=":
                        params.remove(param)
                        break
                break
        # ... and join remaining params + namelist closure
        params.append("/\n")
        param = separator.join(params)
        # Build namelists, set body
        # &fds_label multiparam param /
        if multiparams:
            body = "".join((
                separator.join(("".join((fds_label, multiparam)), param)) for multiparam in multiparams
            ))
        else:
            body = "".join((fds_label, param))
        # Return
        return "".join((info, body))

    def to_fds(self, context):
        """Get my exported FDS string, on error raise BFException."""
        DEBUG and print("BFDS: BFNamelist.to_fds:", self.element)
        # Check self
        if not self.get_exported(context): return None
        try: self.check(context)
        except BFException as err: raise BFException(self, *err.labels)
        # Check and eval related bf_props
        params = list()
        # Export related bf_props
        related_bf_props = list()
        if self.bf_props: related_bf_props.extend(self.bf_props)
        if self.bf_prop_free: related_bf_props.append(self.bf_prop_free)
        for bf_prop in related_bf_props:
            try: param = bf_prop.to_fds(context)
            except BFException as err: raise BFException(self, *err.labels)
            if param: params.append(param)
            self.infos.extend(bf_prop.infos)
        # Return
        return self.format(context, params)

    # Import

    def from_fds(self, context, tokens, snippet=False):
        """Set my properties from imported FDS tokens, on error raise BFException.
        Tokens have the following format: ((fds_original, fds_label, fds_value), ...)
        Eg: (("ID='example'", "ID", "example"), ("XB=...", "XB", (1., 2., 3., 4., 5., 6.,)), ...)
        """
        DEBUG and print("BFDS: BFNamelist.from_fds:", tokens)
        # Init
        if not tokens: return
        # Set separator
        separator = config.namelist_separator
        # If snippet, do not mix old and new properties, so first set default
        # It is really useful only when current Scene is used, but it's fast and snippets are usually short
        if snippet: self.set_default(context)
        # Set export of myself
        self.set_exported(context, True)
        # Order tokens, SURF_ID needs a working mesh, so treat last, after XB, XYZ, PB* that create the mesh
        tokens.sort(key=lambda k:k[1]==("SURF_ID")) # Order is: False then True
        # Treat tokens
        free_texts = list()
        for token in tokens:
            # Init
            fds_original, fds_label, fds_value = token
            # Search managed FDS property, and import token
            try: bf_prop = self.all_bf_props_by_fds_label[fds_label](self.element)
            except KeyError:
                # This FDS property is not managed
                free_texts.append(fds_original)
                continue
            else:
                # This FDS property is managed
                bf_prop.from_fds(context, fds_value) # Do not trap BFException, let it climb up
                continue
        # Save unmanaged tokens in self.bf_prop_free
        if free_texts and self.bf_prop_free:
            self.bf_prop_free.set_value(context, " ".join(free_texts))

# Specialized BFProp and BFNamelist

class BFStringProp(BFProp):
    """BlenderFDS property, interface between a Blender property and an FDS parameter.

    This specialized BFProp is used for single string properties.
    """
    bpy_prop = StringProperty
    bpy_default = ""
    bpy_other =  {"maxlen": 32}

    def check(self, context):
        value = self.get_value()
        if '&' in value or '/' in value:
            raise BFException(self, "& and / characters not allowed")
        if "'" in value or '"' in value or "`" in value or "“" in value \
            or "”" in value or "‘" in value or "’‌" in value:
            raise BFException(self, "Quote characters not allowed")

    def format(self, context, value):
        if value:
            if self.fds_label: return "{}='{}'".format(self.fds_label, value)
            else: return str(value)


class BFBoolProp(BFProp):
    """BlenderFDS property, interface between a Blender property and an FDS parameter.

    This specialized BFProp is used for bool properties, that should not be exported when their value is the same as FDS default.
    """
    bpy_prop = BoolProperty
    bpy_default = False

    def get_exported(self, context):
        if self.bf_prop_export: return self.bf_prop_export.get_value()
        if self.get_value() == self.bpy_default: return False
        return True    
        

class BFExportProp(BFProp):
    """BlenderFDS property, interface between a Blender property and an FDS parameter.

    This specialized BFProp is used for exporting properties.
    """
    label = "Export"
    description = "Set if exported to FDS"
    bpy_type = None # Remember to setup!
    bpy_idname = "bf_export"
    bpy_prop = BoolProperty
    bpy_default = False


class BFFYIProp(BFStringProp):
    """BlenderFDS property, interface between a Blender property and an FDS parameter.

    This specialized BFProp is used for FYI properties.
    """
    label = "FYI"
    description = "Description, for your information"
    fds_label = "FYI"
    bpy_type = None # Remember!
    bpy_idname = "bf_fyi"
    bpy_prop = StringProperty
    bpy_default = ""
    bpy_other =  {"maxlen": 128}

    def _draw_body(self, context, layout):
        row = layout.row()
        row.prop(self.element, self.bpy_idname, text="", icon="INFO")


class BFFreeProp(BFProp):
    """BlenderFDS property, interface between a Blender property and an FDS parameter.

    This specialized BFProp is used for Free parameters properties.
    """
    label = "Free parameters"
    description = "Free parameters, use matched single quotes as string delimiters, eg <P1='example' P2=1,2,3>"
    bpy_type = None # Remember to setup!
    bpy_idname = "bf_free"
    bpy_prop = StringProperty
    bpy_default = ""
    bpy_other =  {"maxlen": 1024}

    def check(self, context):
        value = self.get_value()
        if '&' in value or '/' in value:
            raise BFException(self, "& and / characters not allowed")
        if "`" in value or "‘" in value or "’‌" in value \
            or '"' in value or "”" in value or value.count("'") % 2 != 0:
            raise BFException(self, "Only use matched single quotes as 'string' delimiters")

    def _draw_body(self, context, layout):
        row = layout.row()
        row.prop(self.element, self.bpy_idname, text="", icon="TEXT")

    def format(self, context, value):
        return str(value) or None


class BFNoAutoUIMod(): # No automatic UI
    def draw(self, context, layout):
        pass


class BFNoAutoExportMod(): # No automatic export
    def to_fds(self, context):
        pass


class BFNoAutoMod(BFNoAutoUIMod, BFNoAutoExportMod):
    pass

