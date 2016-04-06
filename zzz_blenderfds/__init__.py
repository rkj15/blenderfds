#    BlenderFDS, an open tool for the NIST Fire Dynamics Simulator
#    Copyright (C) 2013  Emanuele Gissi, http://www.blenderfds.org
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""BlenderFDS"""

print("""
    BlenderFDS  Copyright (C) 2013-2016 Emanuele Gissi, http://www.blenderfds.org
    This addon comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to redistribute it
    under certain conditions; see included license file for details.
""")

bl_info = {
    "name": "BlenderFDS",
    "author": "Emanuele Gissi",
    "version": (4,0,7),
    "blender": (2,7,6),
    "api": 35622,
    "location": "File > Export > FDS Case (.fds)",
    "description": "BlenderFDS, an open graphical editor for the NIST Fire Dynamics Simulator",
    "warning": "",
    "wiki_url": "http://www.blenderfds.org/",
    "tracker_url": "https://github.com/firetools/blenderfds/issues",
    "support": "COMMUNITY",
    "category": "Import-Export",
}

### Import

import bpy
from .types import BFNamelist, BFProp
from .fds import lang # Import the FDS language
from .bl import ui, handlers

### Registration/Unregistration

def register():
    """Register Blender types"""
    # Register module
    bpy.utils.register_module(__name__)    
    # Register all BFProps
    for bf_namelist in BFNamelist.all: bf_namelist.register() # may contain a bpy_idname
    for bf_prop in BFProp.all: bf_prop.register()    
    # Blender things
    ui.register()
    handlers.register()

def unregister():
    """Unregister Blender types"""
    # Blender things
    ui.unregister()
    handlers.unregister()
    bpy.utils.unregister_module(__name__)
    # Unregister all bf_namelists
    for bf_namelist in BFProp.all: bf_namelist.unregister()

if __name__ == "__main__":
    register()
