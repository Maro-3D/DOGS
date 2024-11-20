bl_info = {
    "name": "DOGS",
    "description": (
        "This add-on provides a comprehensive suite of tools for managing and "
        "editing armatures and meshes in Blender. Features include adding and "
        "configuring predefined armature types (Basic, Extended, and Digitigrade), "
        "performing advanced mesh editing operations, and managing bone collections "
        "with enhanced controls for rigging. Additionally, it offers "
        "detailed scene and armature statistics, optimized for both PC and Portable "
        "platforms, to help users maintain performance-friendly models."
    ),
    "author": "Marek Hanzelka",
    "version": (0, 0, 1),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > DOGS",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Rigging",
}

import bpy
from . import operators
from . import panels
from . import properties
from . import utils

# Global variable for keymaps
addon_keymaps = []

def register_shortcuts():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    if kc:  # Ensure the addon keyconfig exists
        # Create a keymap for Weight Paint mode
        km = kc.keymaps.new(name='Weight Paint', space_type='EMPTY')

        # Add keymap item for Alt+Q
        kmi = km.keymap_items.new("object.toggle_weight_paint_mode", 'Q', 'PRESS', alt=True)
        kmi.properties.trigger_from_ui = False  # Ensure the property is set for shortcut context

        addon_keymaps.append((km, kmi))


def unregister_shortcuts():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    # Remove all keymaps added by this addon
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


def register():
    # Register properties
    properties.register()

    # Register operator classes
    for cls in operators.classes:
        bpy.utils.register_class(cls)

    # Register panel classes
    for cls in panels.classes:
        bpy.utils.register_class(cls)

    # Register shortcuts
    register_shortcuts()


def unregister():
    # Unregister shortcuts
    unregister_shortcuts()

    # Unregister panel classes
    for cls in reversed(panels.classes):
        bpy.utils.unregister_class(cls)

    # Unregister operator classes
    for cls in reversed(operators.classes):
        bpy.utils.unregister_class(cls)

    # Unregister properties
    properties.unregister()


if __name__ == "__main__":
    register()
